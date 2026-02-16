from django.urls import path

from .views import CompanyCreateView, CompanySettingsAddView

urlpatterns = [
    path("", CompanyCreateView.as_view(), name="create-company"),
    path("settings/", CompanySettingsAddView.as_view(), name="company-settings"),
]
