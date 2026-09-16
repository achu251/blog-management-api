import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])


def _to_post_out(post: models.Post, db: Session) -> schemas.PostOut:
    """Attach like_count and comment_count to a Post before returning it."""
    like_count = db.query(models.Like).filter(models.Like.post_id == post.id).count()
    comment_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
    return schemas.PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        image_url=post.image_url,
        author_id=post.author_id,
        created_at=post.created_at,
        like_count=like_count,
        comment_count=comment_count,
    )

def _save_image(image: UploadFile) -> str:
    filename = f"{uuid.uuid4()}_{image.filename}"
    filepath = os.path.join("media", "posts", filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return f"/media/posts/{filename}"


def _get_post_or_404(post_id: int, db: Session) -> models.Post:
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# ---- Public endpoints (no login required) ----

@router.get("", response_model=schemas.PaginatedPostOut)
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Post)
    if search:
        query = query.filter(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%")
            )
        )
    
    total_count = query.count()
    total_pages = (total_count + limit - 1) // limit
    
    posts = query.order_by(models.Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return schemas.PaginatedPostOut(
        posts=[_to_post_out(p, db) for p in posts],
        total_count=total_count,
        total_pages=total_pages,
        current_page=page
    )


@router.get("/mine", response_model=list[schemas.PostOut])
def list_my_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # NOTE: this route is declared BEFORE "/{post_id}" so "mine" is not
    # mistakenly parsed as a post_id.
    posts = (
        db.query(models.Post)
        .filter(models.Post.author_id == current_user.id)
        .order_by(models.Post.created_at.desc())
        .all()
    )
    return [_to_post_out(p, db) for p in posts]


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    return _to_post_out(post, db)


# ---- Protected endpoints (login required) ----

@router.post("", response_model=schemas.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    image_url = _save_image(image) if image else None

    new_post = models.Post(
        title=title,
        content=content,
        image_url=image_url,
        author_id=current_user.id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return _to_post_out(new_post, db)


@router.put("/{post_id}", response_model=schemas.PostOut)
def update_post(
    post_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = _get_post_or_404(post_id, db)

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts",
        )

    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    if image is not None:
        post.image_url = _save_image(image)

    db.commit()
    db.refresh(post)
    return _to_post_out(post, db)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = _get_post_or_404(post_id, db)

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts",
        )

    db.delete(post)
    db.commit()
    return None
