from fastapi import FastAPI

from . import models
from .database import engine
from .routers import auth, posts, comments, likes

# Creates blog.db and all tables (users, posts, comments, likes) if they
# don't already exist. Safe to call every time the app starts.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog Management API",
    description="A mini blogging system with JWT auth, posts, comments, and likes.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Blog Management API is running. Visit /docs for Swagger UI."}
