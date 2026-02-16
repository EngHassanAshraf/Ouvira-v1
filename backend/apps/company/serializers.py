from rest_framework.serializers import ModelSerializer
from apps.company.models import Company, CompanySettings


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "name",
            "description",
            "logo",
            "address",
            "status",
            "create_by",
        ]


class CompanySettingsSerializer(ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = [
            "company",
            "default_language",
            "default_currency",
            "timezone",
            "fiscal_year_start_month",
            "feature_flags",
        ]
