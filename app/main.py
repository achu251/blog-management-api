from fastapi import FastAPI

from . import models
from .database import engine, SessionLocal
from .routers import auth, posts, comments, likes, subscriptions

from fastapi.staticfiles import StaticFiles
import os
import sqlite3

# Create media directory if it doesn't exist
os.makedirs("media/posts", exist_ok=True)
os.makedirs("media/invoices", exist_ok=True)

# Auto-migrate: Add image_url column if it doesn't exist
try:
    conn = sqlite3.connect("blog.db")
    conn.execute("ALTER TABLE posts ADD COLUMN image_url VARCHAR;")
    conn.commit()
    conn.close()
except Exception:
    pass

# Auto-migrate: Add plan_id column if it doesn't exist
try:
    conn = sqlite3.connect("blog.db")
    conn.execute("ALTER TABLE users ADD COLUMN plan_id INTEGER REFERENCES subscription_plans(id);")
    conn.commit()
    conn.close()
except Exception:
    pass

models.Base.metadata.create_all(bind=engine)

def create_default_plans():
    db = SessionLocal()
    try:
        if not db.query(models.SubscriptionPlan).first():
            plans = [
                models.SubscriptionPlan(name="Basic", price=0.0, post_limit=1, image_limit=1, like_limit=5, comment_limit=5),
                models.SubscriptionPlan(name="Premium", price=9.99, post_limit=2, image_limit=2, like_limit=20, comment_limit=20),
                models.SubscriptionPlan(name="Pro", price=19.99, post_limit=-1, image_limit=-1, like_limit=-1, comment_limit=-1)
            ]
            db.add_all(plans)
            db.commit()
    finally:
        db.close()

create_default_plans()

app = FastAPI(
    title="Blog Management API",
    description="A mini blogging system with JWT auth, posts, comments, and likes.",
    version="1.0.0",
)

app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(subscriptions.router)

from .admin import setup_admin

@app.on_event("startup")
def startup_event():
    setup_admin(app, engine)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Blog Management API is running. Visit /docs for Swagger UI or /admin for Admin UI."}
