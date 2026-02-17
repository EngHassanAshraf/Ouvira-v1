"""
Security Audit Log Service — business logic for security audit operations.
"""
import logging
from django.db.models import QuerySet

from ..models import SecurityAuditLog

logger = logging.getLogger(__name__)


class SecurityAuditLogService:
    """Service for security audit log operations."""

    @staticmethod
    def get_logs_for_user(user) -> QuerySet:
        """Get security audit logs for a specific user, newest first."""
        return SecurityAuditLog.objects.filter(
            user=user,
        ).select_related("date").order_by("-created_at")

    @staticmethod
    def log_security_event(
        user,
        date_dim,
        action: str,
        metadata: dict = None,
        ip_address: str = None,
    ) -> SecurityAuditLog:
        """Log a security event."""
        log = SecurityAuditLog.objects.create(
            user=user,
            date=date_dim,
            action=action,
            metadata=metadata or {},
            ip_address=ip_address,
        )
        logger.info(f"Security event logged: {action} for user {user}")
        return log
