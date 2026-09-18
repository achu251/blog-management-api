from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..email_utils import notify_new_comment
from .posts import check_limit

router = APIRouter(prefix="/posts", tags=["Comments"])


@router.get("/{post_id}/comments", response_model=list[schemas.CommentOut])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return (
        db.query(models.Comment)
        .filter(models.Comment.post_id == post_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )


@router.post(
    "/{post_id}/comments",
    response_model=schemas.CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    post_id: int,
    comment_in: schemas.CommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    plan = current_user.plan
    if plan:
        comment_count = db.query(models.Comment).filter(models.Comment.user_id == current_user.id).count()
        check_limit(plan.comment_limit, comment_count)

    new_comment = models.Comment(
        post_id=post_id,
        user_id=current_user.id,
        text=comment_in.text,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Notify the post owner by email (skip if commenting on your own post).
    # Runs in the background so the API response isn't delayed by "sending" the email.
    if post.author_id != current_user.id:
        background_tasks.add_task(
            notify_new_comment,
            post.author.email,
            current_user.username,
            post.title,
        )

    return new_comment
