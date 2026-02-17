"""
Activity Log Service — business logic for activity log operations.
"""
import logging
from django.db.models import QuerySet

from ..models import ActivityLog

logger = logging.getLogger(__name__)


class ActivityLogService:
    """Service for activity log operations."""

    @staticmethod
    def get_activity_logs_for_company(company_id: int) -> QuerySet:
        """Get activity logs for a company, newest first."""
        return ActivityLog.objects.filter(
            company_id=company_id,
        ).select_related("user", "date").order_by("-created_at")

    @staticmethod
    def get_activity_logs_for_user(user) -> QuerySet:
        """Get activity logs for a specific user."""
        return ActivityLog.objects.filter(
            user=user,
        ).select_related("company", "date").order_by("-created_at")

    @staticmethod
    def log_activity(
        user,
        company,
        date_dim,
        entity_type: str,
        entity_id: int,
        action: str,
        old_values: dict = None,
        new_values: dict = None,
        ip_address: str = None,
    ) -> ActivityLog:
        """Log an activity."""
        log = ActivityLog.objects.create(
            user=user,
            company=company,
            date=date_dim,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
        logger.info(f"Activity logged: {action} by {user} on {entity_type}:{entity_id}")
        return log
