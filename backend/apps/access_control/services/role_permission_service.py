"""
Role Permission Service - Handles role-permission assignments
"""
import logging
from django.utils import timezone
from django.db.models import QuerySet

from ..models import RolePermission, Role, Permission, UserCompany
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class RolePermissionService:
    """Service for role-permission operations"""

    @staticmethod
    def get_user_company_ids(user) -> QuerySet:
        """Get active company IDs for a user"""
        return UserCompany.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).values_list("company_id", flat=True)

    @staticmethod
    def get_role_permissions_for_user(user, role_id: int = None) -> QuerySet:
        """
        Get role permissions accessible to a user.
        
        Args:
            user: User instance
            role_id: Optional role ID to filter by
            
        Returns:
            QuerySet of RolePermission instances
        """
        user_companies = RolePermissionService.get_user_company_ids(user)
        
        queryset = RolePermission.objects.filter(
            role__company__in=user_companies,
            is_deleted=False,
            role__is_deleted=False
        )
        
        if role_id:
            queryset = queryset.filter(role_id=role_id, role__is_deleted=False)
        
        return queryset

    @staticmethod
    def get_role_permission(pk: int, user=None) -> RolePermission:
        """
        Get a specific role permission by ID.
        
        Args:
            pk: RolePermission primary key
            user: Optional user to verify access
            
        Returns:
            RolePermission instance
        """
        role_permission = RolePermission.objects.get(
            pk=pk,
            is_deleted=False,
            role__is_deleted=False
        )
        
        # Verify user has access if provided
        if user:
            user_companies = RolePermissionService.get_user_company_ids(user)
            if role_permission.role.company_id not in user_companies:
                raise BusinessException("You don't have access to this role permission.")
        
        return role_permission

    @staticmethod
    def assign_permission_to_role(role: Role, permission: Permission, granted: bool = True) -> RolePermission:
        """
        Assign a permission to a role.
        
        Args:
            role: Role instance
            permission: Permission instance
            granted: Whether permission is granted
            
        Returns:
            Created RolePermission instance
        """
        role_permission, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
            defaults={"granted": granted, "is_deleted": False}
        )
        
        if not created and role_permission.is_deleted:
            role_permission.is_deleted = False
            role_permission.granted = granted
            role_permission.save()
        
        logger.info(f"Permission {permission.code} assigned to role {role.role}")
        return role_permission

    @staticmethod
    def update_role_permission(role_permission: RolePermission, granted: bool = None) -> RolePermission:
        """
        Update a role permission.
        
        Args:
            role_permission: RolePermission instance to update
            granted: Whether permission is granted
            
        Returns:
            Updated RolePermission instance
        """
        if granted is not None:
            role_permission.granted = granted
        role_permission.save()
        logger.info(f"Role permission updated: {role_permission}")
        return role_permission

    @staticmethod
    def remove_permission_from_role(role_permission: RolePermission) -> None:
        """
        Remove a permission from a role (soft delete).
        
        Args:
            role_permission: RolePermission instance to remove
        """
        role_permission.deleted_at = timezone.now()
        role_permission.is_deleted = True
        role_permission.save()
        logger.info(f"Permission removed from role: {role_permission}")
