"""
Permission Service - Handles permission operations
"""
import logging
from django.utils import timezone
from django.db.models import QuerySet

from ..models import Permission
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for permission operations"""

    @staticmethod
    def get_active_permissions() -> QuerySet:
        """Get all non-deleted permissions"""
        return Permission.objects.filter(is_deleted=False).order_by("code")

    @staticmethod
    def get_permission(pk: int) -> Permission:
        """
        Get a specific permission by ID.
        
        Args:
            pk: Permission primary key
            
        Returns:
            Permission instance
            
        Raises:
            Permission.DoesNotExist: If permission not found
        """
        return Permission.objects.get(pk=pk, is_deleted=False)

    @staticmethod
    def create_permission(code: str, module: str, description: str = "") -> Permission:
        """
        Create a new permission.
        
        Args:
            code: Permission code (unique identifier)
            module: Module name
            description: Optional description
            
        Returns:
            Created Permission instance
        """
        permission = Permission.objects.create(
            code=code,
            module=module,
            description=description
        )
        logger.info(f"Permission created: {code}")
        return permission

    @staticmethod
    def update_permission(permission: Permission, **kwargs) -> Permission:
        """
        Update a permission.
        
        Args:
            permission: Permission instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated Permission instance
        """
        for key, value in kwargs.items():
            setattr(permission, key, value)
        permission.save()
        logger.info(f"Permission updated: {permission.code}")
        return permission

    @staticmethod
    def soft_delete_permission(permission: Permission) -> None:
        """
        Soft delete a permission.
        
        Args:
            permission: Permission instance to delete
        """
        permission.deleted_at = timezone.now()
        permission.is_deleted = True
        permission.save()
        logger.info(f"Permission soft deleted: {permission.code}")
