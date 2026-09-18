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

def check_limit(limit: int, current_count: int):
    if limit != -1 and current_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You’ve reached your plan limit. Kindly upgrade your plan to continue."
        )


def _to_post_out(post: models.Post, db: Session) -> schemas.PostOut:
    """Attach like_count and comment_count to a Post before returning it."""
    like_count = db.query(models.Like).filter(models.Like.post_id == post.id).count()
    comment_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
    image_urls = [img.image_url for img in post.images] if hasattr(post, 'images') else []
    return schemas.PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        image_url=post.image_url,
        image_urls=image_urls,
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
    images: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    plan = current_user.plan
    if plan:
        post_count = db.query(models.Post).filter(models.Post.author_id == current_user.id).count()
        check_limit(plan.post_limit, post_count)

    all_images = [img for img in images if img.filename]
    if image and image.filename:
        all_images.insert(0, image)
        
    if plan and all_images:
        check_limit(plan.image_limit, len(all_images) - 1)  # if checking exact amount, or just check len vs limit
        # Better: check len(all_images) against limit
        if plan.image_limit != -1 and len(all_images) > plan.image_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You’ve reached your plan limit. Kindly upgrade your plan to continue."
            )

    main_image_url = _save_image(all_images[0]) if all_images else None

    new_post = models.Post(
        title=title,
        content=content,
        image_url=main_image_url,
        author_id=current_user.id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    for img in all_images:
        url = _save_image(img)
        post_img = models.PostImage(post_id=new_post.id, image_url=url)
        db.add(post_img)
    db.commit()
    db.refresh(new_post)

    return _to_post_out(new_post, db)


@router.put("/{post_id}", response_model=schemas.PostOut)
def update_post(
    post_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    images: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = _get_post_or_404(post_id, db)

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts",
        )

    all_images = [img for img in images if img.filename]
    if image and image.filename:
        all_images.insert(0, image)

    plan = current_user.plan
    if plan and all_images:
        current_image_count = db.query(models.PostImage).filter(models.PostImage.post_id == post.id).count()
        new_count = current_image_count + len(all_images)
        if plan.image_limit != -1 and new_count > plan.image_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You’ve reached your plan limit. Kindly upgrade your plan to continue."
            )

    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    if all_images:
        post.image_url = _save_image(all_images[0])
        for img in all_images:
            url = _save_image(img)
            post_img = models.PostImage(post_id=post.id, image_url=url)
            db.add(post_img)

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
