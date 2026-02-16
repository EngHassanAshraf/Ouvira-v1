"""
Login Activity Service - Handles login activity tracking
"""
import logging
from django.utils import timezone

from ..models import LoginActivity
from apps.identity.account.models.user import CustomUser

logger = logging.getLogger(__name__)


class LoginActivityService:
    """Service for tracking login activities"""

    @staticmethod
    def get_client_ip(request) -> str:
        """
        Extract client IP address from request.
        
        Args:
            request: Django request object
            
        Returns:
            IP address string
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip

    @staticmethod
    def record_login(user: CustomUser, request) -> LoginActivity:
        """
        Record a login activity.
        
        Args:
            user: User instance
            request: Django request object
            
        Returns:
            Created LoginActivity instance
        """
        ip_address = LoginActivityService.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        
        activity = LoginActivity.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        logger.info(f"Login activity recorded for user: {user.primary_mobile} from IP: {ip_address}")
        return activity
