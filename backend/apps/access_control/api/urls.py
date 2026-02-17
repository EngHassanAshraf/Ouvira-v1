from django.urls import path

from .views import (
    # Permission views
    PermissionListCreateView,
    PermissionDetailView,
    # Role views
    RoleListCreateView,
    RoleDetailView,
    # RolePermission views
    RolePermissionListCreateView,
    RolePermissionDetailView,
    # UserCompany views
    UserCompanyListCreateView,
    UserCompanyDetailView,
    # UserCompanyRole views
    UserCompanyRoleListCreateView,
    UserCompanyRoleDetailView,
    # Invitation views
    InvitationListCreateView,
    InvitationDetailView,
    InvitationAcceptView,
    InvitationRevokeView,
    InvitationResendView,
)

urlpatterns = [
    # Permission endpoints
    path("permissions/", PermissionListCreateView.as_view(), name="permission-list-create"),
    path("permissions/<int:pk>/", PermissionDetailView.as_view(), name="permission-detail"),

    # Role endpoints
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),

    # RolePermission endpoints
    path("role-permissions/", RolePermissionListCreateView.as_view(), name="role-permission-list-create"),
    path("role-permissions/<int:pk>/", RolePermissionDetailView.as_view(), name="role-permission-detail"),

    # UserCompany endpoints
    path("user-companies/", UserCompanyListCreateView.as_view(), name="user-company-list-create"),
    path("user-companies/<int:pk>/", UserCompanyDetailView.as_view(), name="user-company-detail"),

    # UserCompanyRole endpoints
    path("user-company-roles/", UserCompanyRoleListCreateView.as_view(), name="user-company-role-list-create"),
    path("user-company-roles/<int:pk>/", UserCompanyRoleDetailView.as_view(), name="user-company-role-detail"),

    # Invitation endpoints
    path("invitations/", InvitationListCreateView.as_view(), name="invitation-list-create"),
    path("invitations/<int:pk>/", InvitationDetailView.as_view(), name="invitation-detail"),
    path("invitations/<int:pk>/revoke/", InvitationRevokeView.as_view(), name="invitation-revoke"),
    path("invitations/<int:pk>/resend/", InvitationResendView.as_view(), name="invitation-resend"),
    path("invitations/accept/", InvitationAcceptView.as_view(), name="invitation-accept"),
]
