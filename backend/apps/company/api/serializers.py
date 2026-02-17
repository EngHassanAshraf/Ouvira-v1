"""
Company serializers with validations.
"""
from rest_framework import serializers
from apps.company.models import Company, CompanySettings


class CompanySettingsSerializer(serializers.ModelSerializer):
    """Serializer for CompanySettings (nested or standalone)"""

    class Meta:
        model = CompanySettings
        fields = [
            "id",
            "company",
            "default_language",
            "default_currency",
            "timezone",
            "fiscal_year_start_month",
            "feature_flags",
            "updated_at",
        ]
        read_only_fields = ["id", "company", "updated_at"]

    def validate_fiscal_year_start_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value


class CompanyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing companies."""

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "logo",
            "status",
            "is_parent_company",
            "created_at",
        ]
        read_only_fields = fields


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for company detail/create/update."""
    settings = CompanySettingsSerializer(read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "logo",
            "create_by",
            "parent_company",
            "is_parent_company",
            "description",
            "address",
            "status",
            "settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "create_by", "settings", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Company name must be at least 2 characters.")

        # Check uniqueness (exclude current instance on update)
        qs = Company.objects.filter(name__iexact=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

    def validate_status(self, value):
        # Only allow valid transitions
        if self.instance:
            current = self.instance.status
            valid_transitions = {
                Company.Status.ACTIVE: [Company.Status.DEACTIVATED],
                Company.Status.DEACTIVATED: [Company.Status.ACTIVE, Company.Status.DELETED],
            }
            allowed = valid_transitions.get(current, [])
            if value not in allowed and value != current:
                raise serializers.ValidationError(
                    f"Cannot transition from '{current}' to '{value}'."
                )
        return value

    def validate_parent_company(self, value):
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("A company cannot be its own parent.")
        return value

    def create(self, validated_data):
        validated_data["create_by"] = self.context["request"].user
        return super().create(validated_data)
