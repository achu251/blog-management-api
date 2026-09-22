from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users & Dashboard"])

@router.get("/dashboard/data", response_model=schemas.DashboardDataOut)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Total posts created by user
    user_posts = db.query(models.Post).filter(models.Post.author_id == current_user.id).all()
    total_posts = len(user_posts)
    
    # Total comments made by user
    total_comments_made = db.query(models.Comment).filter(models.Comment.user_id == current_user.id).count()
    
    # Calculate stats per post and total likes/views
    total_likes_received = 0
    total_post_views = 0
    post_stats = []
    
    for post in user_posts:
        views = post.views or 0
        total_post_views += views
        
        # Likes on this post
        likes_count = db.query(models.Like).filter(models.Like.post_id == post.id).count()
        total_likes_received += likes_count
        
        # Comments on this post
        comments_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
        
        post_stats.append(schemas.DashboardPostStats(
            post_id=post.id,
            post_title=post.title,
            views=views,
            likes_count=likes_count,
            comments_count=comments_count
        ))
        
    return schemas.DashboardDataOut(
        total_posts=total_posts,
        total_comments_made=total_comments_made,
        total_likes_received=total_likes_received,
        total_post_views=total_post_views,
        post_stats=post_stats
    )
