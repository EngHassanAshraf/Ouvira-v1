"""
Company Service — business logic for Company and CompanySettings operations.
"""
import logging
from django.utils import timezone
from django.db.models import QuerySet

from ..models import Company, CompanySettings
from apps.access_control.models import UserCompany, UserCompanyRole
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for Company operations"""

    @staticmethod
    def get_user_company_ids(user) -> QuerySet:
        """Get active company IDs for a user."""
        return UserCompany.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
        ).values_list("company_id", flat=True)

    @staticmethod
    def get_companies_for_user(user) -> QuerySet:
        """Get companies accessible to a user."""
        company_ids = CompanyService.get_user_company_ids(user)
        print("company_ids", company_ids)
        return Company.objects.filter(
            id__in=company_ids,
            is_deleted=False,
        ).order_by("-created_at")

    @staticmethod
    def get_company(pk: int, user=None) -> Company:
        """
        Get a specific company by ID.

        Raises:
            Company.DoesNotExist: If company not found
            BusinessException: If user doesn't have access
        """
        company = Company.objects.get(pk=pk, is_deleted=False)

        if user:
            company_ids = CompanyService.get_user_company_ids(user)
            if company.id not in company_ids:
                raise BusinessException("You don't have access to this company.")

        return company

    @staticmethod
    def create_company(name: str, created_by, **kwargs) -> Company:
        """Create a new company."""
        company = Company.objects.create(
            name=name,
            create_by=created_by,
            **kwargs,
        )
        logger.info(f"Company created: {name} by user {created_by}")
        return company

    @staticmethod
    def update_company(company: Company, **kwargs) -> Company:
        """Update a company."""
        for key, value in kwargs.items():
            setattr(company, key, value)
        company.save()
        logger.info(f"Company updated: {company.name}")
        return company

    @staticmethod
    def soft_delete_company(company: Company) -> None:
        """Soft delete a company."""
        company.status = Company.Status.DELETED
        company.is_deleted = True
        company.deleted_at = timezone.now()
        company.save()
        logger.info(f"Company soft deleted: {company.name}")

    @staticmethod
    def is_company_owner(user, company: Company) -> bool:
        """Check if user is the creator of the company."""
        return company.create_by_id == user.id

    @staticmethod
    def is_company_admin(user, company_id: int) -> bool:
        """Check if user has admin role in a company."""
        return UserCompanyRole.objects.filter(
            user_company__user=user,
            user_company__company_id=company_id,
            user_company__is_active=True,
            user_company__is_deleted=False,
            role__role__iexact="admin",
            role__is_deleted=False,
            is_deleted=False,
        ).exists()


class CompanySettingsService:
    """Service for CompanySettings operations"""

    @staticmethod
    def get_or_create_settings(company: Company) -> CompanySettings:
        """Get or create settings for a company."""
        settings, created = CompanySettings.objects.get_or_create(
            company=company,
            defaults={
                "default_language": "en",
                "default_currency": "USD",
                "timezone": "UTC",
                "fiscal_year_start_month": 1,
                "feature_flags": {},
            },
        )
        if created:
            logger.info(f"Default settings created for company: {company.name}")
        return settings

    @staticmethod
    def update_settings(settings: CompanySettings, **kwargs) -> CompanySettings:
        """Update company settings."""
        for key, value in kwargs.items():
            setattr(settings, key, value)
        settings.save()
        logger.info(f"Settings updated for company: {settings.company.name}")
        return settings
