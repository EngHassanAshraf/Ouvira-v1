"""
User Company Role Service - Handles user-company-role assignments
"""
import logging
from django.utils import timezone
from django.db.models import QuerySet

from ..models import UserCompanyRole, UserCompany, Role
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class UserCompanyRoleService:
    """Service for user-company-role operations"""

    @staticmethod
    def get_user_company_ids(user) -> QuerySet:
        """Get active UserCompany IDs for a user"""
        return UserCompany.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).values_list("id", flat=True)

    @staticmethod
    def get_user_company_roles_for_user(user, user_company_id: int = None, role_id: int = None) -> QuerySet:
        """
        Get user-company-role assignments accessible to a user.
        
        Args:
            user: User instance
            user_company_id: Optional UserCompany ID to filter by
            role_id: Optional Role ID to filter by
            
        Returns:
            QuerySet of UserCompanyRole instances
        """
        user_companies = UserCompanyRoleService.get_user_company_ids(user)
        
        queryset = UserCompanyRole.objects.filter(
            user_company__in=user_companies,
            is_deleted=False,
            user_company__is_deleted=False,
            user_company__is_active=True,
            role__is_deleted=False
        )
        
        if user_company_id:
            queryset = queryset.filter(user_company_id=user_company_id)
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        
        return queryset

    @staticmethod
    def get_user_company_role(pk: int, user=None) -> UserCompanyRole:
        """
        Get a specific user-company-role assignment.
        
        Args:
            pk: UserCompanyRole primary key
            user: Optional user to verify access
            
        Returns:
            UserCompanyRole instance
        """
        user_company_role = UserCompanyRole.objects.get(
            pk=pk,
            is_deleted=False,
            user_company__is_deleted=False,
            user_company__is_active=True,
            role__is_deleted=False
        )
        
        # Verify user has access if provided
        if user:
            user_companies = UserCompanyRoleService.get_user_company_ids(user)
            if user_company_role.user_company_id not in user_companies:
                raise BusinessException("You don't have access to this assignment.")
        
        return user_company_role

    @staticmethod
    def assign_role_to_user(user_company: UserCompany, role: Role) -> UserCompanyRole:
        """
        Assign a role to a user in a company.
        
        Args:
            user_company: UserCompany instance
            role: Role instance
            
        Returns:
            Created UserCompanyRole instance
        """
        # Validate role belongs to user's company
        if role.company is not None and role.company != user_company.company:
            raise BusinessException("Role does not belong to the user's company.")
        
        user_company_role, created = UserCompanyRole.objects.get_or_create(
            user_company=user_company,
            role=role,
            defaults={"is_deleted": False}
        )
        
        if not created and user_company_role.is_deleted:
            user_company_role.is_deleted = False
            user_company_role.save()
        
        logger.info(f"Role {role.role} assigned to user {user_company.user.primary_mobile} in company {user_company.company.name}")
        return user_company_role

    @staticmethod
    def remove_role_from_user(user_company_role: UserCompanyRole) -> None:
        """
        Remove a role from a user (soft delete).
        
        Args:
            user_company_role: UserCompanyRole instance to remove
        """
        user_company_role.deleted_at = timezone.now()
        user_company_role.is_deleted = True
        user_company_role.save()
        logger.info(f"Role removed from user: {user_company_role}")
