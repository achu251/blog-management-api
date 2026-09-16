from fastapi import FastAPI

from . import models
from .database import engine
from .routers import auth, posts, comments, likes

from fastapi.staticfiles import StaticFiles
import os
import sqlite3

# Create media directory if it doesn't exist
os.makedirs("media/posts", exist_ok=True)

# Auto-migrate: Add image_url column if it doesn't exist
try:
    conn = sqlite3.connect("blog.db")
    conn.execute("ALTER TABLE posts ADD COLUMN image_url VARCHAR;")
    conn.commit()
    conn.close()
except Exception:
    pass

models.Base.metadata.create_all(bind=engine)

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


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Blog Management API is running. Visit /docs for Swagger UI."}
