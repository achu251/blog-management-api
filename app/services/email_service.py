
"""
Reusable SMTP email service.

Email configuration is loaded from environment variables.
SMTP failures are handled gracefully so they never crash the API.
"""

import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


LOG_FILE = "email_log.txt"


def _log_email_failure(
    to_email: str,
    subject: str,
    body: str,
    reason: str,
) -> None:
    """
    Log email failures instead of allowing them to crash the API.
    """

    entry = (
        f"\n--- EMAIL NOT SENT ---\n"
        f"Time: {datetime.now().isoformat()}\n"
        f"To: {to_email}\n"
        f"Subject: {subject}\n"
        f"Reason: {reason}\n"
        f"Body:\n{body}\n"
        f"----------------------\n"
    )

    print(entry)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(entry)
    except Exception as log_error:
        print(f"[email log error] {log_error}")


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    """
    Send a plain-text email using SMTP.

    This function is designed to run through FastAPI BackgroundTasks.
    """

    if not EMAIL_ADDRESS:
        _log_email_failure(
            to_email,
            subject,
            body,
            "EMAIL_ADDRESS is not configured",
        )
        return

    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        _log_email_failure(
            to_email,
            subject,
            body,
            "EMAIL_USERNAME or EMAIL_PASSWORD is not configured",
        )
        return

    message = EmailMessage()

    message["From"] = EMAIL_ADDRESS
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=15,
        ) as server:

            server.starttls(context=context)

            server.login(
                EMAIL_USERNAME,
                EMAIL_PASSWORD,
            )

            server.send_message(message)

        print(
            f"[email sent] "
            f"to={to_email} "
            f"subject='{subject}'"
        )

    except Exception as error:
        _log_email_failure(
            to_email,
            subject,
            body,
            f"SMTP error: {error}",
        )

