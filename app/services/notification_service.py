
"""
Application-level notification logic.

This module prepares notification content and delegates
actual email delivery to email_service.py.
"""

from datetime import datetime

from .email_service import send_email


def notify_post_owner(
    owner_email: str,
    actor_username: str,
    post_title: str,
    activity_type: str,
    activity_time: datetime,
) -> None:
    """
    Send a notification when somebody interacts with a post.
    """

    formatted_time = activity_time.strftime(
        "%Y-%m-%d %I:%M %p"
    )

    if activity_type == "Comment":
        activity_message = "commented on your post"

    elif activity_type == "Like":
        activity_message = "liked your post"

    else:
        activity_message = "interacted with your post"

    subject = f"New {activity_type.lower()} on your post"

    body = (
        "Hello,\n\n"
        "There has been new activity on your blog post.\n\n"
        f"Post: {post_title}\n"
        f"User: {actor_username}\n"
        f"Activity: {activity_message}\n"
        f"Time: {formatted_time}\n\n"
        "Thank you,\n"
        "Blog Management API"
    )

    send_email(
        to_email=owner_email,
        subject=subject,
        body=body,
    )

