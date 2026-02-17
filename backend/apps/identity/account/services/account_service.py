"""
Account Service — business logic for user account operations.
"""
import logging
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models.user import CustomUser
from apps.shared.exceptions import BusinessException
from apps.shared.messages.error import ERROR_MESSAGES

logger = logging.getLogger(__name__)


class AccountService:
    """Service for user account operations."""

    @staticmethod
    def get_profile(user: CustomUser) -> CustomUser:
        """Get the user profile."""
        return user

    @staticmethod
    def update_profile(user: CustomUser, **data) -> CustomUser:
        """
        Update user profile fields.

        Allowed fields: full_name, email.
        Password changes go through a separate flow.
        """
        allowed_fields = {"full_name", "email"}
        for key, value in data.items():
            if key in allowed_fields:
                setattr(user, key, value)

        user.save()
        logger.info(f"Profile updated for user {user.username}")
        return user

    @staticmethod
    def list_users(company_id: int = None) -> QuerySet:
        """
        List active users. Optionally filter by company membership.
        """
        from apps.access_control.models import UserCompany

        qs = CustomUser.objects.filter(is_active=True, is_deleted=False)

        if company_id:
            user_ids = UserCompany.objects.filter(
                company_id=company_id,
                is_active=True,
                is_deleted=False,
            ).values_list("user_id", flat=True)
            qs = qs.filter(id__in=user_ids)

        return qs.order_by("-date_joined")

    @staticmethod
    def update_existing_user(**data) -> CustomUser:
        """
        Update an existing user found by phone number.
        Used during OTP-based signup finalization.
        """
        primary_mobile = data.get("primary_mobile")
        user = CustomUser.objects.filter(primary_mobile=primary_mobile).first()

        if not user:
            raise BusinessException(ERROR_MESSAGES["ACCOUNT_NOT_FOUND"])

        password = data.pop("password", None)

        for key, value in data.items():
            setattr(user, key, value)

        if password:
            user.set_password(password)
        user.save()

        return user
