"""
Account serializers for user profile and admin user listing.
"""
import re
from rest_framework import serializers
from apps.identity.account.models.user import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    """Full user profile serializer (for the authenticated user)."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "full_name",
            "email",
            "primary_mobile",
            "email_verified",
            "phone_verified",
            "account_uid",
            "is_2fa_enabled",
            "two_fa_type",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "username",
            "primary_mobile",
            "email_verified",
            "phone_verified",
            "account_uid",
            "is_2fa_enabled",
            "two_fa_type",
            "date_joined",
            "last_login",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (limited fields)."""

    class Meta:
        model = CustomUser
        fields = ["full_name", "email"]

    def validate_full_name(self, value):
        value = value.strip()
        if not re.match(r"^[A-Za-z\s]+$", value):
            raise serializers.ValidationError(
                "Name must contain only letters and spaces."
            )
        if len(value) < 3:
            raise serializers.ValidationError(
                "Name must be at least 3 characters."
            )
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        qs = CustomUser.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email is already in use.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for admin user listings."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "full_name",
            "email",
            "primary_mobile",
            "is_active",
            "date_joined",
        ]
        read_only_fields = fields
