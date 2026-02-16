from django.urls import path
from .views import ChangeUserRoleView, SessionTestAPIView


urlpatterns = [
    path(
        "user/<int:user_id>/change-role/",
        ChangeUserRoleView.as_view(),
        name="change_user_role",
    ),
    path("session-tests/", SessionTestAPIView.as_view(), name="session-tests"),
]
