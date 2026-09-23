from sqlalchemy.orm import Session

from .. import models


def create_in_app_notification(
    db: Session,
    user_id: int,
    message: str,
    notification_type: str,
):
    """
    Create an in-app notification for a specific user.
    """

    notification = models.Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=0,
    )

    db.add(notification)

    return notification