from django.urls import path

from .views import CompanyListCreateView, CompanyDetailView, CompanySettingsView

urlpatterns = [
    path("", CompanyListCreateView.as_view(), name="company-list-create"),
    path("<int:pk>/", CompanyDetailView.as_view(), name="company-detail"),
    path("<int:pk>/settings/", CompanySettingsView.as_view(), name="company-settings"),
]
