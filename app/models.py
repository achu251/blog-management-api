from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    post_limit = Column(Integer, nullable=False) # -1 for unlimited
    image_limit = Column(Integer, nullable=False) # -1 for unlimited
    like_limit = Column(Integer, nullable=False) # -1 for unlimited
    comment_limit = Column(Integer, nullable=False) # -1 for unlimited


class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    price = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    transaction_id = Column(String, nullable=False)
    invoice_pdf_path = Column(String, nullable=False)

    user = relationship("User", back_populates="billing_history")
    plan = relationship("SubscriptionPlan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
     # Auth0 social login information
    auth0_id = Column(String, unique=True, index=True, nullable=True)
    auth_provider = Column(String, nullable=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=True)

    plan = relationship("SubscriptionPlan")
    billing_history = relationship("BillingHistory", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    ai_chats = relationship(
        "AIChat",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    views = Column(Integer, default=0, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")


class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    image_url = Column(String, nullable=False)

    post = relationship("Post", back_populates="images")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # A user can only like a given post once
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_post_user_like"),)

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    message = Column(String, nullable=False)

    notification_type = Column(
        String,
        nullable=False,
        default="general",
    )

    is_read = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )


class AIChat(Base):
    __tablename__ = "ai_chats"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    question = Column(String, nullable=False)

    ai_response = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="ai_chats",
    )
