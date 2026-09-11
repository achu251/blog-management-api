"""
Real email notification utility using SMTP (Gmail by default).

Credentials are loaded from a .env file (never hardcoded, never committed
to git). See README.md for how to set EMAIL_ADDRESS / EMAIL_APP_PASSWORD.

If the .env values are missing, we fall back to logging the email to
email_log.txt instead of crashing the app -- so the API still runs even
before you've configured email.
"""

import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the project root, if present

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

LOG_FILE = "email_log.txt"


def _log_fallback(to_email: str, subject: str, body: str, reason: str) -> None:
    entry = (
        f"\n--- EMAIL NOT SENT ({reason}) AT {datetime.now().isoformat()} ---\n"
        f"To: {to_email}\nSubject: {subject}\nBody: {body}\n"
        f"----------------------------------------\n"
    )
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry)


def send_email(to_email: str, subject: str, body: str) -> None:
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        _log_fallback(to_email, subject, body, reason="EMAIL_ADDRESS/EMAIL_APP_PASSWORD not set in .env")
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"[email sent] to={to_email} subject='{subject}'")
    except Exception as e:
        # Never let an email failure crash the API request that triggered it.
        _log_fallback(to_email, subject, body, reason=f"SMTP error: {e}")


def notify_new_comment(post_owner_email: str, commenter_username: str, post_title: str) -> None:
    send_email(
        to_email=post_owner_email,
        subject=f"New comment on your post '{post_title}'",
        body=f"{commenter_username} commented on your post '{post_title}'.",
    )


def notify_new_like(post_owner_email: str, liker_username: str, post_title: str) -> None:
    send_email(
        to_email=post_owner_email,
        subject=f"New like on your post '{post_title}'",
        body=f"{liker_username} liked your post '{post_title}'.",
    )