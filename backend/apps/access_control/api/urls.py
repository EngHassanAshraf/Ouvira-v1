from django.urls import path

from .views import (
    # Permission views
    PermissionListView,
    PermissionCreateView,
    PermissionRetrieveView,
    PermissionUpdateView,
    PermissionDeleteView,
    # Role views
    RoleListView,
    RoleCreateView,
    RoleRetrieveView,
    RoleUpdateView,
    RoleDeleteView,
    # RolePermission views
    RolePermissionListView,
    RolePermissionCreateView,
    RolePermissionRetrieveView,
    RolePermissionUpdateView,
    RolePermissionDeleteView,
    # UserCompany views
    UserCompanyListView,
    UserCompanyCreateView,
    UserCompanyRetrieveView,
    UserCompanyUpdateView,
    UserCompanyDeleteView,
    # UserCompanyRole views
    UserCompanyRoleListView,
    UserCompanyRoleCreateView,
    UserCompanyRoleRetrieveView,
    UserCompanyRoleUpdateView,
    UserCompanyRoleDeleteView,
    # Invitation views
    InvitationListView,
    InvitationCreateView,
    InvitationRetrieveView,
    InvitationUpdateView,
    InvitationDeleteView,
    InvitationAcceptView,
    InvitationRevokeView,
    InvitationResendView,
)

urlpatterns = [
    # Permission endpoints
    # GET /permissions/ -> list, POST /permissions/ -> create
    path("permissions/", PermissionListView.as_view(), name="permission-list"),
    path("permissions/", PermissionCreateView.as_view(), name="permission-create"),
    # GET /permissions/<pk>/ -> retrieve, PUT/PATCH /permissions/<pk>/ -> update, DELETE /permissions/<pk>/ -> delete
    path("permissions/<int:pk>/", PermissionRetrieveView.as_view(), name="permission-retrieve"),
    path("permissions/<int:pk>/", PermissionUpdateView.as_view(), name="permission-update"),
    path("permissions/<int:pk>/", PermissionDeleteView.as_view(), name="permission-delete"),
    
    # Role endpoints
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("roles/", RoleCreateView.as_view(), name="role-create"),
    path("roles/<int:pk>/", RoleRetrieveView.as_view(), name="role-retrieve"),
    path("roles/<int:pk>/", RoleUpdateView.as_view(), name="role-update"),
    path("roles/<int:pk>/", RoleDeleteView.as_view(), name="role-delete"),
    
    # RolePermission endpoints
    path("role-permissions/", RolePermissionListView.as_view(), name="role-permission-list"),
    path("role-permissions/", RolePermissionCreateView.as_view(), name="role-permission-create"),
    path("role-permissions/<int:pk>/", RolePermissionRetrieveView.as_view(), name="role-permission-retrieve"),
    path("role-permissions/<int:pk>/", RolePermissionUpdateView.as_view(), name="role-permission-update"),
    path("role-permissions/<int:pk>/", RolePermissionDeleteView.as_view(), name="role-permission-delete"),
    
    # UserCompany endpoints
    path("user-companies/", UserCompanyListView.as_view(), name="user-company-list"),
    path("user-companies/", UserCompanyCreateView.as_view(), name="user-company-create"),
    path("user-companies/<int:pk>/", UserCompanyRetrieveView.as_view(), name="user-company-retrieve"),
    path("user-companies/<int:pk>/", UserCompanyUpdateView.as_view(), name="user-company-update"),
    path("user-companies/<int:pk>/", UserCompanyDeleteView.as_view(), name="user-company-delete"),
    
    # UserCompanyRole endpoints
    path("user-company-roles/", UserCompanyRoleListView.as_view(), name="user-company-role-list"),
    path("user-company-roles/", UserCompanyRoleCreateView.as_view(), name="user-company-role-create"),
    path("user-company-roles/<int:pk>/", UserCompanyRoleRetrieveView.as_view(), name="user-company-role-retrieve"),
    path("user-company-roles/<int:pk>/", UserCompanyRoleUpdateView.as_view(), name="user-company-role-update"),
    path("user-company-roles/<int:pk>/", UserCompanyRoleDeleteView.as_view(), name="user-company-role-delete"),
    
    # Invitation endpoints
    path("invitations/", InvitationListView.as_view(), name="invitation-list"),
    path("invitations/", InvitationCreateView.as_view(), name="invitation-create"),
    path("invitations/<int:pk>/", InvitationRetrieveView.as_view(), name="invitation-retrieve"),
    path("invitations/<int:pk>/", InvitationUpdateView.as_view(), name="invitation-update"),
    path("invitations/<int:pk>/", InvitationDeleteView.as_view(), name="invitation-delete"),
    path("invitations/<int:pk>/revoke/", InvitationRevokeView.as_view(), name="invitation-revoke"),
    path("invitations/<int:pk>/resend/", InvitationResendView.as_view(), name="invitation-resend"),
    path("invitations/accept/", InvitationAcceptView.as_view(), name="invitation-accept"),
]
