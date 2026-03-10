"""
Notification Service — business logic for notifications.
"""
import logging
from django.db.models import QuerySet
from apps.shared.services.email_service import send_email
from ..models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification operations."""

    @staticmethod
    def get_user_notifications(user) -> QuerySet:
        """Get all notifications for a user, newest first."""
        return Notification.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    def get_unread_count(user) -> int:
        """Get count of unread notifications."""
        return Notification.objects.filter(user=user, read=False).count()

    @staticmethod
    def mark_as_read(notification_id: int, user) -> Notification:
        """Mark a single notification as read."""
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.read = True
        notification.save(update_fields=["read"])
        return notification

    @staticmethod
    def mark_all_read(user) -> int:
        """Mark all notifications as read. Returns count of updated."""
        count = Notification.objects.filter(
            user=user, read=False
        ).update(read=True)
        logger.info(f"Marked {count} notifications as read for user {user}")
        return count

    @staticmethod
    def create_notification(user, message: str) -> Notification:
        notification = Notification.objects.create(
            user=user,
            message=message
        )
        # email notification
        if user.email:
            try:
                send_email(
                    subject="New Notification",
                    message=message,
                    recipient_email=user.email
                )
            except Exception as e:
                logger.error(f"Email notification failed for {user.email}: {e}")
        return notification
