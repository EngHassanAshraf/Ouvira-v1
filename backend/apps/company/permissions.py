"""
Company permissions.
"""
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.access_control.models import UserCompanyRole


class IsCompanyOwner(BasePermission):
    """
    Allows access only to the user who created the company.
    Expects the view to have the company object available via get_object().
    """
    message = "Only the company owner can perform this action."

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        return obj.create_by_id == request.user.id


class IsCompanyAdmin(BasePermission):
    """
    Allows access to users who have an 'admin' role in the target company.
    Resolves company_id from: URL kwargs (pk), request body, or query params.
    """
    message = "You must be an admin of this company."

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # Try to get company_id from URL, body, or query params
        company_id = (
            view.kwargs.get("pk")
            or request.data.get("company")
            or request.query_params.get("company")
        )

        if not company_id:
            return False

        try:
            return UserCompanyRole.objects.filter(
                user_company__user=request.user,
                user_company__company_id=company_id,
                user_company__is_active=True,
                user_company__is_deleted=False,
                role__role__iexact="admin",
                role__is_deleted=False,
                is_deleted=False,
            ).exists()
        except Exception:
            return False

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        """Check admin role for the specific company object."""
        try:
            return UserCompanyRole.objects.filter(
                user_company__user=request.user,
                user_company__company_id=obj.id,
                user_company__is_active=True,
                user_company__is_deleted=False,
                role__role__iexact="admin",
                role__is_deleted=False,
                is_deleted=False,
            ).exists()
        except Exception:
            return False
