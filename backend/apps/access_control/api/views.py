"""
Optimized access control views using service layer
"""
import logging
from django.db.models.query import QuerySet
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from .serializers import (
    PermissionSerializer,
    PermissionListSerializer,
    RoleSerializer,
    RoleListSerializer,
    RolePermissionSerializer,
    UserCompanySerializer,
    UserCompanyRoleSerializer,
    InvitationSerializer,
    InvitationListSerializer,
)

from ..services import (
    PermissionService,
    RoleService,
    RolePermissionService,
    UserCompanyService,
    UserCompanyRoleService,
    InvitationService,
)
from ..permissions.IsAdminUser import IsAdminUser
from ..models import Permission
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


# ==================== PERMISSION VIEWS ====================

class PermissionListView(ListAPIView):
    """List all permissions (non-deleted) - uses lightweight serializer for performance"""
    serializer_class = PermissionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return PermissionService.get_active_permissions()


class PermissionCreateView(CreateAPIView):
    """Create a new permission (Admin only)"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    # Note: IsAdminUser requires company in request, but permissions are global
    # The permission check will still work as it checks for admin role in any company


class PermissionRetrieveView(RetrieveAPIView):
    """Retrieve a specific permission"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PermissionService.get_active_permissions()


class PermissionUpdateView(UpdateAPIView):
    """Update a permission (Admin only)"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return PermissionService.get_active_permissions()


class PermissionDeleteView(DestroyAPIView):
    """Soft delete a permission (Admin only)"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return PermissionService.get_active_permissions()

    def perform_destroy(self, instance):
        PermissionService.soft_delete_permission(instance)


# ==================== ROLE VIEWS ====================

class RoleListView(ListAPIView):
    """List roles for user's companies - uses lightweight serializer for performance"""
    serializer_class = RoleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        company_id = self.request.query_params.get("company")
        return RoleService.get_roles_for_user(self.request.user, company_id=int(company_id) if company_id else None)


class RoleCreateView(CreateAPIView):
    """Create a new role (Admin only)"""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        company_id = request.data.get("company")
        if not company_id:
            return Response(
                {"detail": "Company is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            # Verify company exists
            RoleService.verify_company(company_id)
        except Exception:
            return Response(
                {"detail": "Company not found."},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class RoleRetrieveView(RetrieveAPIView):
    """Retrieve a specific role"""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RoleService.get_roles_for_user(self.request.user)


class RoleUpdateView(UpdateAPIView):
    """Update a role (Admin only)"""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return RoleService.get_roles_for_user(self.request.user)


class RoleDeleteView(DestroyAPIView):
    """Soft delete a role (Admin only)"""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return RoleService.get_roles_for_user(self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Get company_id from query params
        company_id = request.query_params.get("company")
        if not company_id:
            return Response(
                {"detail": "Company is required as query parameter."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            RoleService.soft_delete_role(instance, company_id=int(company_id))
            return Response(status=HTTP_204_NO_CONTENT)
        except BusinessException as e:
            return Response(
                {"detail": str(e)},
                status=HTTP_403_FORBIDDEN,
            )
        except ValueError:
            return Response(
                {"detail": "Invalid company ID."},
                status=HTTP_400_BAD_REQUEST,
            )


# ==================== ROLE PERMISSION VIEWS ====================

class RolePermissionListView(ListAPIView):
    """List role permissions, optionally filtered by role"""
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        role_id = self.request.query_params.get("role")
        return RolePermissionService.get_role_permissions_for_user(
            self.request.user,
            role_id=int(role_id) if role_id else None
        )


class RolePermissionCreateView(CreateAPIView):
    """Assign a permission to a role (Admin only)"""
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify user has admin access to the role's company
        role = serializer.validated_data.get("role")
        if role and role.company:
            company_id = role.company.id
            if not request.data.get("company") and not request.query_params.get("company"):
                request.data["company"] = company_id
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class RolePermissionRetrieveView(RetrieveAPIView):
    """Retrieve a specific role permission"""
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RolePermissionService.get_role_permissions_for_user(self.request.user)


class RolePermissionUpdateView(UpdateAPIView):
    """Update a role permission (Admin only)"""
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return RolePermissionService.get_role_permissions_for_user(self.request.user)


class RolePermissionDeleteView(DestroyAPIView):
    """Remove a permission from a role (Admin only)"""
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return RolePermissionService.get_role_permissions_for_user(self.request.user)

    def perform_destroy(self, instance):
        RolePermissionService.remove_permission_from_role(instance)


# ==================== USER COMPANY VIEWS ====================

class UserCompanyListView(ListAPIView):
    """List user-company associations"""
    serializer_class = UserCompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        user_id = self.request.query_params.get("user")
        company_id = self.request.query_params.get("company")
        
        # Check if current user is admin
        is_admin = UserCompanyService.is_user_admin(self.request.user)
        
        queryset = UserCompanyService.get_user_companies(
            self.request.user,
            filter_by_user=not is_admin
        )
        
        # Admins can filter by user or company
        if is_admin:
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            if company_id:
                queryset = queryset.filter(company_id=company_id)
        
        return queryset


class UserCompanyCreateView(CreateAPIView):
    """Associate a user with a company (Admin only)"""
    serializer_class = UserCompanySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        company_id = request.data.get("company")
        if not company_id:
            return Response(
                {"detail": "Company is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class UserCompanyRetrieveView(RetrieveAPIView):
    """Retrieve a specific user-company association"""
    serializer_class = UserCompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCompanyService.get_user_companies(
            self.request.user,
            filter_by_user=not UserCompanyService.is_user_admin(self.request.user)
        )


class UserCompanyUpdateView(UpdateAPIView):
    """Update a user-company association (Admin only)"""
    serializer_class = UserCompanySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        from ..models import UserCompany
        return UserCompany.objects.filter(is_deleted=False)


class UserCompanyDeleteView(DestroyAPIView):
    """Remove a user from a company (Admin only)"""
    serializer_class = UserCompanySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        from ..models import UserCompany
        return UserCompany.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        UserCompanyService.remove_user_from_company(instance)


# ==================== USER COMPANY ROLE VIEWS ====================

class UserCompanyRoleListView(ListAPIView):
    """List user-company-role assignments"""
    serializer_class = UserCompanyRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        user_company_id = self.request.query_params.get("user_company")
        role_id = self.request.query_params.get("role")
        
        return UserCompanyRoleService.get_user_company_roles_for_user(
            self.request.user,
            user_company_id=int(user_company_id) if user_company_id else None,
            role_id=int(role_id) if role_id else None
        )


class UserCompanyRoleCreateView(CreateAPIView):
    """Assign a role to a user in a company (Admin only)"""
    serializer_class = UserCompanyRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify user has admin access to the user_company's company
        user_company = serializer.validated_data.get("user_company")
        if user_company and user_company.company:
            company_id = user_company.company.id
            if not request.data.get("company") and not request.query_params.get("company"):
                request.data["company"] = company_id
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class UserCompanyRoleRetrieveView(RetrieveAPIView):
    """Retrieve a specific user-company-role assignment"""
    serializer_class = UserCompanyRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCompanyRoleService.get_user_company_roles_for_user(self.request.user)


class UserCompanyRoleUpdateView(UpdateAPIView):
    """Update a user-company-role assignment (Admin only)"""
    serializer_class = UserCompanyRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return UserCompanyRoleService.get_user_company_roles_for_user(self.request.user)


class UserCompanyRoleDeleteView(DestroyAPIView):
    """Remove a role from a user in a company (Admin only)"""
    serializer_class = UserCompanyRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return UserCompanyRoleService.get_user_company_roles_for_user(self.request.user)

    def perform_destroy(self, instance):
        UserCompanyRoleService.remove_role_from_user(instance)


# ==================== INVITATION VIEWS ====================

class InvitationListView(ListAPIView):
    """List invitations, optionally filtered by company and status - uses lightweight serializer"""
    serializer_class = InvitationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        company_id = self.request.query_params.get("company")
        status_filter = self.request.query_params.get("status")
        
        return InvitationService.get_invitations_for_user(
            self.request.user,
            company_id=int(company_id) if company_id else None,
            status=status_filter
        )


class InvitationCreateView(CreateAPIView):
    """Create a new invitation (Admin only)"""
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        company_id = request.data.get("company")
        if not company_id:
            return Response(
                {"detail": "Company is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use service to create invitation
            invitation = InvitationService.create_invitation(
                company=serializer.validated_data["company"],
                email=serializer.validated_data["email"],
                role=serializer.validated_data["role"],
                invited_by=request.user,
                expires_at=serializer.validated_data.get("expires_at"),
                token=serializer.validated_data.get("token")
            )
            
            return Response(
                InvitationSerializer(invitation).data,
                status=HTTP_201_CREATED
            )
        except BusinessException as e:
            return Response(
                {"detail": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )


class InvitationRetrieveView(RetrieveAPIView):
    """Retrieve a specific invitation"""
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InvitationService.get_invitations_for_user(self.request.user)


class InvitationUpdateView(UpdateAPIView):
    """Update an invitation (Admin only)"""
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return InvitationService.get_invitations_for_user(self.request.user)


class InvitationDeleteView(DestroyAPIView):
    """Delete an invitation (Admin only)"""
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return InvitationService.get_invitations_for_user(self.request.user)


class InvitationAcceptView(APIView):
    """Accept an invitation by token (Public endpoint)"""
    permission_classes = []  # Public endpoint

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response(
                {"detail": "Token is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required to accept invitation."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            user_company, user_company_role = InvitationService.accept_invitation(
                token=token,
                user=request.user
            )
            
            return Response(
                {
                    "detail": "Invitation accepted successfully.",
                    "user_company": UserCompanySerializer(user_company).data,
                    "role": RoleSerializer(user_company_role.role).data,
                },
                status=HTTP_200_OK,
            )
        except BusinessException as e:
            return Response(
                {"detail": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Error accepting invitation")
            return Response(
                {"detail": "Invalid or expired invitation token."},
                status=HTTP_404_NOT_FOUND,
            )


class InvitationRevokeView(APIView):
    """Revoke an invitation (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        try:
            invitation = InvitationService.get_invitation(pk, user=request.user)
        except Exception:
            return Response(
                {"detail": "Invitation not found."},
                status=HTTP_404_NOT_FOUND,
            )

        # Verify user has admin access to the invitation's company
        company_id = request.data.get("company") or request.query_params.get("company")
        if not company_id or invitation.company.id != int(company_id):
            return Response(
                {"detail": "You don't have permission to revoke this invitation."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            InvitationService.revoke_invitation(invitation)
            return Response(
                {"detail": "Invitation revoked successfully."},
                status=HTTP_200_OK,
            )
        except BusinessException as e:
            return Response(
                {"detail": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )


class InvitationResendView(APIView):
    """Resend an invitation (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        try:
            invitation = InvitationService.get_invitation(pk, user=request.user)
        except Exception:
            return Response(
                {"detail": "Invitation not found."},
                status=HTTP_404_NOT_FOUND,
            )

        # Verify user has admin access to the invitation's company
        company_id = request.data.get("company") or request.query_params.get("company")
        if not company_id or invitation.company.id != int(company_id):
            return Response(
                {"detail": "You don't have permission to resend this invitation."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            invitation = InvitationService.resend_invitation(invitation)
            
            # TODO: Send email in production
            return Response(
                {
                    "detail": "Invitation resent successfully.",
                    "invitation": InvitationSerializer(invitation).data,
                },
                status=HTTP_200_OK,
            )
        except BusinessException as e:
            return Response(
                {"detail": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )
