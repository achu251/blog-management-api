from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from datetime import datetime
from ..services.notification_service import notify_post_owner
from .posts import check_limit

router = APIRouter(prefix="/posts", tags=["Likes"])


@router.post("/{post_id}/like", response_model=schemas.LikeOut)
def toggle_like(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Toggle behaviour: calling this endpoint once LIKES the post.
    Calling it again (by the same user) UNLIKES it. This is what the
    task means by "like and unlike posts" using one clean action.
    """
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_like = (
        db.query(models.Like)
        .filter(models.Like.post_id == post_id, models.Like.user_id == current_user.id)
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        db.commit()
        liked = False
        message = "Post unliked"
    else:
        plan = current_user.plan
        if plan:
            like_count = db.query(models.Like).filter(models.Like.user_id == current_user.id).count()
            check_limit(plan.like_limit, like_count)
            
        new_like = models.Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        liked = True
        message = "Post liked"

        if post.author_id != current_user.id:
         background_tasks.add_task(
        notify_post_owner,
        post.author.email,
        current_user.username,
        post.title,
        "Like",
        datetime.now(),
    )

    like_count = db.query(models.Like).filter(models.Like.post_id == post_id).count()
    return schemas.LikeOut(liked=liked, like_count=like_count, message=message)
