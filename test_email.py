import os
import sys
from dotenv import load_dotenv

# load .env
load_dotenv()

from app.services.notification_service import notify_post_owner
from datetime import datetime

print("Sending test email...")

try:
    notify_post_owner(
        owner_email=os.getenv("EMAIL_ADDRESS"),
        actor_username="john_doe",
        post_title="FastAPI Best Practices",
        activity_type="Comment",
        activity_time=datetime.now()
    )
    print("Test email function executed.")
except Exception as e:
    print(f"Error: {e}")
