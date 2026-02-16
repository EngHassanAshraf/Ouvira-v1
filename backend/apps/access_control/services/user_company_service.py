"""
User Company Service - Handles user-company associations
"""
import logging
from django.utils import timezone
from django.db.models import QuerySet

from ..models import UserCompany, UserCompanyRole
from apps.identity.account.models import CustomUser
from apps.company.models import Company
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class UserCompanyService:
    """Service for user-company operations"""

    @staticmethod
    def is_user_admin(user) -> bool:
        """
        Check if user is admin in any company.
        
        Args:
            user: User instance
            
        Returns:
            True if user is admin, False otherwise
        """
        return UserCompanyRole.objects.filter(
            user_company__user=user,
            user_company__is_active=True,
            user_company__is_deleted=False,
            role__role__iexact="admin",
            role__is_deleted=False,
            is_deleted=False
        ).exists()

    @staticmethod
    def get_user_companies(user, filter_by_user: bool = True) -> QuerySet:
        """
        Get user-company associations.
        
        Args:
            user: User instance
            filter_by_user: If True, only return associations for this user
            
        Returns:
            QuerySet of UserCompany instances
        """
        queryset = UserCompany.objects.filter(is_deleted=False)
        
        if filter_by_user and not UserCompanyService.is_user_admin(user):
            queryset = queryset.filter(user=user)
        
        return queryset.filter(is_active=True)

    @staticmethod
    def get_user_company(pk: int, user=None) -> UserCompany:
        """
        Get a specific user-company association.
        
        Args:
            pk: UserCompany primary key
            user: Optional user to verify access
            
        Returns:
            UserCompany instance
        """
        user_company = UserCompany.objects.get(pk=pk, is_deleted=False)
        
        # Verify user has access if provided
        if user and not UserCompanyService.is_user_admin(user):
            if user_company.user != user:
                raise BusinessException("You don't have access to this association.")
        
        return user_company

    @staticmethod
    def associate_user_with_company(user: CustomUser, company: Company, is_primary: bool = False) -> UserCompany:
        """
        Associate a user with a company.
        
        Args:
            user: User instance
            company: Company instance
            is_primary: Whether this is the primary company
            
        Returns:
            Created UserCompany instance
        """
        user_company, created = UserCompany.objects.get_or_create(
            user=user,
            company=company,
            defaults={
                "is_primary_company": is_primary,
                "is_active": True,
                "is_deleted": False
            }
        )
        
        if not created and user_company.is_deleted:
            user_company.is_deleted = False
            user_company.is_active = True
            user_company.save()
        
        logger.info(f"User {user.primary_mobile} associated with company {company.name}")
        return user_company

    @staticmethod
    def update_user_company(user_company: UserCompany, **kwargs) -> UserCompany:
        """
        Update a user-company association.
        
        Args:
            user_company: UserCompany instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated UserCompany instance
        """
        for key, value in kwargs.items():
            setattr(user_company, key, value)
        user_company.save()
        logger.info(f"UserCompany updated: {user_company}")
        return user_company

    @staticmethod
    def remove_user_from_company(user_company: UserCompany) -> None:
        """
        Remove a user from a company (soft delete).
        
        Args:
            user_company: UserCompany instance to remove
        """
        user_company.deleted_at = timezone.now()
        user_company.is_deleted = True
        user_company.is_active = False
        user_company.save()
        logger.info(f"User removed from company: {user_company}")
