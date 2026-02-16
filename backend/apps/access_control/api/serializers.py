from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.utils import timezone

from ..models import (
    Role,
    Permission,
    RolePermission,
    Invitation,
    UserCompany,
    UserCompanyRole,
)


# ==================== BASE SERIALIZER MIXINS ====================

class SoftDeleteValidationMixin:
    """Mixin to add soft-delete aware validation helpers"""

    def get_instance_value(self, field_name):
        """Get field value from instance if available, otherwise from data"""
        if self.instance:
            return getattr(self.instance, field_name, None)
        # Try to get from initial_data if available (during validation)
        if hasattr(self, 'initial_data') and self.initial_data:
            return self.initial_data.get(field_name)
        return None


class TimestampedFieldsMixin:
    """Mixin to make timestamp fields read-only"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make timestamp fields read-only
        if self.instance is None:
            # On create, make created_at and updated_at read-only
            self.fields.get("created_at", {}).read_only = True
            self.fields.get("updated_at", {}).read_only = True


# ==================== PERMISSION SERIALIZERS ====================

class PermissionSerializer(ModelSerializer, SoftDeleteValidationMixin, TimestampedFieldsMixin):
    class Meta:
        model = Permission
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "deleted_at", "is_deleted")

    def validate_code(self, value):
        """Validate permission code"""
        if not value or not (value := value.strip()):
            raise serializers.ValidationError("Permission code cannot be empty.")
        
        # Check uniqueness excluding soft-deleted records
        qs = Permission.objects.filter(code=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Permission code must be unique.")
        return value

    def validate_module(self, value):
        """Validate module name"""
        if not value or not (value := value.strip()):
            raise serializers.ValidationError("Module cannot be empty.")
        return value


# ==================== ROLE SERIALIZERS ====================

class RoleSerializer(ModelSerializer, SoftDeleteValidationMixin, TimestampedFieldsMixin):
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "deleted_at", "is_deleted")

    def validate_role(self, value):
        """Validate role name"""
        if not value or not (value := value.strip()):
            raise serializers.ValidationError("Role name cannot be empty.")
        if len(value) > 50:
            raise serializers.ValidationError(
                "Role must be at most 50 characters long."
            )
        return value

    def validate(self, data):
        """Validate role uniqueness within company"""
        role_val = data.get("role") or self.get_instance_value("role")
        company = data.get("company") or self.get_instance_value("company")
        
        # Exclude soft-deleted roles when checking for duplicates
        qs = Role.objects.filter(role=role_val, company=company, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"role": "A role with this name already exists for the company."}
            )
        return data


# ==================== ROLE PERMISSION SERIALIZERS ====================

class RolePermissionSerializer(ModelSerializer, SoftDeleteValidationMixin, TimestampedFieldsMixin):
    class Meta:
        model = RolePermission
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "deleted_at", "is_deleted")

    def validate(self, data):
        """Validate role-permission uniqueness"""
        role = data.get("role") or self.get_instance_value("role")
        permission = data.get("permission") or self.get_instance_value("permission")
        
        if not role or not permission:
            raise serializers.ValidationError("Both role and permission are required.")
        
        # Exclude soft-deleted role permissions when checking for duplicates
        qs = RolePermission.objects.filter(
            role=role, 
            permission=permission, 
            is_deleted=False
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This role already has the specified permission."
            )
        return data


# ==================== USER COMPANY SERIALIZERS ====================

class UserCompanySerializer(ModelSerializer, SoftDeleteValidationMixin, TimestampedFieldsMixin):
    class Meta:
        model = UserCompany
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "deleted_at", "is_deleted", "joined_at")

    def validate(self, data):
        """Validate user-company uniqueness"""
        user = data.get("user") or self.get_instance_value("user")
        company = data.get("company") or self.get_instance_value("company")
        
        if not user or not company:
            raise serializers.ValidationError("Both user and company are required.")
        
        # Exclude soft-deleted user-company associations when checking for duplicates
        qs = UserCompany.objects.filter(user=user, company=company, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This user is already associated with the company."
            )
        return data


# ==================== USER COMPANY ROLE SERIALIZERS ====================

class UserCompanyRoleSerializer(ModelSerializer, SoftDeleteValidationMixin, TimestampedFieldsMixin):
    """Serializer for user-company-role assignments"""
    # Include nested representations for read operations (can be optimized in views)
    role = RoleSerializer(read_only=True)
    user_company = UserCompanySerializer(read_only=True)

    class Meta:
        model = UserCompanyRole
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "deleted_at", "is_deleted", "assigned_at")

    def validate(self, data):
        """Validate role belongs to user's company"""
        role = data.get("role") or self.get_instance_value("role")
        user_company = data.get("user_company") or self.get_instance_value("user_company")
        
        if not role or not user_company:
            raise serializers.ValidationError(
                "Both user_company and role are required."
            )
        
        # Validate role belongs to user's company
        if role.company is not None and role.company != user_company.company:
            raise serializers.ValidationError(
                "Role does not belong to the user's company."
            )
        return data


# ==================== INVITATION SERIALIZERS ====================

class InvitationSerializer(ModelSerializer, SoftDeleteValidationMixin, TimestampedFieldsMixin):
    class Meta:
        model = Invitation
        fields = "__all__"
        read_only_fields = ("created_at", "token", "status", "accepted_by")

    def validate_email(self, value):
        """Validate and normalize email"""
        if not value or not (value := value.strip().lower()):
            raise serializers.ValidationError("Email is required.")
        return value

    def validate_expires_at(self, value):
        """Validate expiry is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Expiry must be a future datetime.")
        return value

    def validate(self, data):
        """Validate invitation business rules"""
        company = data.get("company") or self.get_instance_value("company")
        role = data.get("role") or self.get_instance_value("role")
        email = data.get("email") or self.get_instance_value("email")

        if not company:
            raise serializers.ValidationError(
                {"company": "Company is required for an invitation."}
            )

        # Validate role belongs to company
        if role and role.company is not None and role.company != company:
            raise serializers.ValidationError(
                {"role": "Selected role does not belong to the target company."}
            )

        # Check for pending invitations (only if creating new invitation)
        if not self.instance:
            if Invitation.objects.filter(
                email=email, 
                company=company, 
                status="pending"
            ).exists():
                raise serializers.ValidationError(
                    {
                        "email": "There is already a pending invitation for this email and company."
                    }
                )

        # Token validation (only if token is provided)
        token = data.get("token")
        if token:
            qs = Invitation.objects.filter(token=token)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"token": "Token must be unique."})

        return data


# ==================== LIST SERIALIZERS (OPTIMIZED FOR LIST VIEWS) ====================

class RoleListSerializer(ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Role
        fields = ("id", "role", "desc", "company", "is_system_role", "created_at")
        read_only_fields = fields


class PermissionListSerializer(ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Permission
        fields = ("id", "code", "module", "description", "created_at")
        read_only_fields = fields


class InvitationListSerializer(ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Invitation
        fields = (
            "id", 
            "email", 
            "company", 
            "role", 
            "status", 
            "expires_at", 
            "created_at"
        )
        read_only_fields = fields
