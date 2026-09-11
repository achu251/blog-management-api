# Blog Management API

A mini blogging system built with FastAPI + SQLAlchemy + SQLite + JWT auth.

## Features
- JWT authentication (`/auth/register`, `/auth/login`)
- CRUD for blog posts, with ownership checks (only the author can update/delete)
- Comments on posts (public read, authenticated write)
- Like / unlike posts (toggle) with duplicate-like prevention
- Simulated email notifications on new comments and new likes (logged to `email_log.txt`)
- Interactive Swagger docs at `/docs`

## 1. Setup

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be live at: http://127.0.0.1:8000
Swagger UI (interactive docs): http://127.0.0.1:8000/docs

A file called `blog.db` (SQLite database) is created automatically the first
time you run the app — it contains 4 tables: `users`, `posts`, `comments`, `likes`.

## 3. Testing the flow in Swagger UI

1. Open http://127.0.0.1:8000/docs
2. Expand `POST /auth/register` → click "Try it out" → enter a username, email,
   password → Execute. You should get a 201 response with your new user (no password shown).
3. Expand `POST /auth/login` → "Try it out" → enter the SAME username/password in the
   form fields → Execute. Copy the `access_token` from the response.
4. Click the green **"Authorize"** button at the top right of the page.
   Paste the token (just the token, Swagger adds "Bearer " automatically) → Authorize → Close.
5. Now every "lock icon" endpoint will send your token automatically. Try:
   - `POST /posts` to create a post
   - `GET /posts` to see all posts (public, no login needed)
   - `GET /posts/mine` to see only your own posts
   - `PUT /posts/{post_id}` / `DELETE /posts/{post_id}` — only works if you're the author
   - `POST /posts/{post_id}/comments` to comment
   - `GET /posts/{post_id}/comments` to view comments (public)
   - `POST /posts/{post_id}/like` — first call likes, calling it again unlikes
6. Register a SECOND user, log in as them, and try to update/delete the FIRST
   user's post — you should get a `403 Forbidden`. This proves the ownership check works.
7. Check `email_log.txt` in the project folder — you'll see logged "emails"
   for every comment and like made on someone else's post.

## 4. Taking screenshots of the SQLite tables

Any SQLite browser works. Two easy options:

**Option A — DB Browser for SQLite (GUI, recommended)**
1. Download "DB Browser for SQLite" (free): https://sqlitebrowser.org/
2. Open `blog.db`
3. Go to the "Browse Data" tab, pick each table (`users`, `posts`,
   `comments`, `likes`) from the dropdown, and screenshot each.

**Option B — command line**
```bash
sqlite3 blog.db
.headers on
.mode column
SELECT * FROM users;
SELECT * FROM posts;
SELECT * FROM comments;
SELECT * FROM likes;
```
Screenshot the terminal output for each query.

## 5. Project structure

```
blog_api/
├── requirements.txt
├── README.md
├── blog.db              (created automatically on first run)
├── email_log.txt        (created automatically when a notification fires)
└── app/
    ├── main.py           # FastAPI app, includes all routers
    ├── database.py       # SQLAlchemy engine/session setup
    ├── models.py         # User, Post, Comment, Like ORM models
    ├── schemas.py         # Pydantic request/response validation
    ├── security.py       # Password hashing + JWT create/verify
    ├── dependencies.py   # get_current_user() auth dependency
    ├── email_utils.py    # Simulated email notification sender
    └── routers/
        ├── auth.py       # /auth/register, /auth/login
        ├── posts.py      # Post CRUD + /posts/mine
        ├── comments.py   # Comment endpoints
        └── likes.py      # Like/unlike endpoint
```

## 6. How authentication actually works (in plain terms)

1. `/auth/register` hashes your password with bcrypt (via passlib) and stores
   the hash — never the raw password — in the `users` table.
2. `/auth/login` checks your username exists and that bcrypt can verify your
   password against the stored hash. If correct, it creates a JWT containing
   your user id (`sub` claim) signed with a secret key, and returns it.
3. On every protected request, you send `Authorization: Bearer <token>`.
   FastAPI's `OAuth2PasswordBearer` extracts the token, `decode_access_token()`
   verifies the signature and expiry, and `get_current_user()` looks up the
   matching user in the database — that becomes `current_user` in your route.
4. Ownership checks are just a plain `if post.author_id != current_user.id:
   raise 403` — no magic, just comparing IDs already available.

## 7. Notes / things you could extend later
- Swap `email_utils.send_email()` for real SMTP/SendGrid/SES — nothing else
  in the app needs to change.
- Move `SECRET_KEY` in `security.py` into an environment variable for production.
- Add pagination to `GET /posts` if the dataset grows large.
