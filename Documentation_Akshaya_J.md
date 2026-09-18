# Blog Management API - Feature Enhancements
**Author**: Akshaya J, Full Stack Developer

## Overview
This document outlines the recent enhancements made to the Blog Management API, focusing on improving the user experience and content management capabilities. 

## Features Implemented

### 1. Image Uploads for Posts
- **Database Schema**: The `Post` model has been updated to include an `image_url` field.
- **Storage**: Uploaded images are securely saved in the local file system under the `/media/posts/` directory.
- **Endpoints**: 
  - The `POST /posts` and `PUT /posts/{id}` endpoints were updated to accept `multipart/form-data`.
  - Used FastAPI's `UploadFile` to handle file uploads seamlessly.
- **Serving Media**: Configured FastAPI `StaticFiles` to serve uploaded images dynamically, returning relative paths (e.g., `/media/posts/<filename>.jpg`) in the API responses.

### 2. Pagination & Search
- **Pagination**: Added `page` and `limit` query parameters to the `GET /posts` endpoint to ensure efficient loading of posts.
- **Search**: Implemented a `search` query parameter allowing users to find posts by keywords in the title or content. Both pagination and search can be used together.
- **Response Format**: The paginated response returns structured data, including the list of posts, `total_count`, `total_pages`, and `current_page`, to make it easy for frontend applications to integrate.

## API Usage Example

**1. Create a Post with an Image (POST `/posts`)**
- Requires Authentication (JWT Bearer Token).
- Request Body Type: `multipart/form-data`
- Fields: `title` (text), `content` (text), `image` (file).

**2. List Posts with Pagination and Search (GET `/posts`)**
- Example Request: `GET /posts/?page=1&limit=10&search=technology`
- Example Response:
```json
{
  "posts": [
    {
      "id": 1,
      "title": "Technology Trends",
      "content": "Exploring the latest...",
      "image_url": "/media/posts/sample.jpg",
      "author_id": 1,
      "created_at": "2026-09-16T12:00:00Z",
      "like_count": 5,
      "comment_count": 2
    }
  ],
  "total_count": 1,
  "total_pages": 1,
  "current_page": 1
}
```

## Setup & Testing
1. Ensure the Python virtual environment is activated (`venv\Scripts\activate`).
2. Run the application: `uvicorn app.main:app --reload`.
3. Open the Swagger UI at `http://127.0.0.1:8000/docs` to test the endpoints interactively.
