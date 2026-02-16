"""
Role Service - Handles role operations
"""
import logging
from django.utils import timezone
from django.db.models import QuerySet

from ..models import Role, UserCompany
from apps.company.models import Company
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class RoleService:
    """Service for role operations"""

    @staticmethod
    def get_user_company_ids(user) -> QuerySet:
        """
        Get active company IDs for a user.
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of company IDs
        """
        return UserCompany.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).values_list("company_id", flat=True)

    @staticmethod
    def get_roles_for_user(user, company_id: int = None) -> QuerySet:
        """
        Get roles accessible to a user.
        
        Args:
            user: User instance
            company_id: Optional company ID to filter by
            
        Returns:
            QuerySet of Role instances
        """
        user_companies = RoleService.get_user_company_ids(user)
        
        queryset = Role.objects.filter(
            company__in=user_companies,
            is_deleted=False
        )
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        return queryset.order_by("role")

    @staticmethod
    def get_role(pk: int, user=None) -> Role:
        """
        Get a specific role by ID.
        
        Args:
            pk: Role primary key
            user: Optional user to verify access
            
        Returns:
            Role instance
            
        Raises:
            Role.DoesNotExist: If role not found
        """
        role = Role.objects.get(pk=pk, is_deleted=False)
        
        # Verify user has access if provided
        if user:
            user_companies = RoleService.get_user_company_ids(user)
            if role.company_id not in user_companies:
                raise BusinessException("You don't have access to this role.")
        
        return role

    @staticmethod
    def verify_company(company_id: int) -> Company:
        """
        Verify company exists and is not soft-deleted.
        
        Args:
            company_id: Company primary key
            
        Returns:
            Company instance
            
        Raises:
            Company.DoesNotExist: If company not found
        """
        return Company.objects.get(pk=company_id, is_deleted=False)

    @staticmethod
    def create_role(role: str, company_id: int = None, desc: str = "", is_system_role: bool = False) -> Role:
        """
        Create a new role.
        
        Args:
            role: Role name
            company_id: Optional company ID (None for system roles)
            desc: Role description
            is_system_role: Whether this is a system role
            
        Returns:
            Created Role instance
        """
        company = None
        if company_id:
            company = RoleService.verify_company(company_id)
        
        role_instance = Role.objects.create(
            role=role,
            company=company,
            desc=desc,
            is_system_role=is_system_role
        )
        
        logger.info(f"Role created: {role} for company: {company_id}")
        return role_instance

    @staticmethod
    def update_role(role: Role, **kwargs) -> Role:
        """
        Update a role.
        
        Args:
            role: Role instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated Role instance
        """
        # Verify company if being updated
        if "company" in kwargs and kwargs["company"]:
            RoleService.verify_company(kwargs["company"].id)
        
        for key, value in kwargs.items():
            setattr(role, key, value)
        role.save()
        logger.info(f"Role updated: {role.role}")
        return role

    @staticmethod
    def soft_delete_role(role: Role, company_id: int = None) -> None:
        """
        Soft delete a role.
        
        Args:
            role: Role instance to delete
            company_id: Optional company ID for validation
            
        Raises:
            BusinessException: If trying to delete system role or invalid company
        """
        # Prevent deletion of system roles
        if role.company is None:
            raise BusinessException("Cannot delete system roles.")
        
        # Verify company if provided
        if company_id and role.company.id != company_id:
            raise BusinessException("Role not found for this company.")
        
        role.deleted_at = timezone.now()
        role.is_deleted = True
        role.save()
        logger.info(f"Role soft deleted: {role.role}")
