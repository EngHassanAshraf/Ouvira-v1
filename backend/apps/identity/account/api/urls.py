from django.urls import path
from .views import UserProfileView, UserListView, SessionTestAPIView

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("session-tests/", SessionTestAPIView.as_view(), name="session-tests"),
]
