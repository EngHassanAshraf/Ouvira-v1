from django.urls import path

from apps.core.views import RoleCreateView, RoleListView, RoleDeleteView

urlpatterns = [
    path("roles/", RoleCreateView.as_view(), name="create-role"),
    path("roles/", RoleListView.as_view(), name="list-roles"),
    path("roles/<pk>", RoleDeleteView.as_view(), name="delete-role"),
]
