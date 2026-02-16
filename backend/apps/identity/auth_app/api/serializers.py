import re

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers


from apps.identity.account.models.user import CustomUser

from ..utils import validate_user_email, validate_user_password, validate_user_mobile
from ..utilits import verify_turnstile


class BaseUserInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(min_length=3, max_length=255, allow_blank=False)

    primary_mobile = serializers.CharField(max_length=13, allow_blank=False)

    def validate_full_name(self, value):
        if not re.match(r"^[A-Za-z\s]+$", value):
            raise serializers.ValidationError(
                "The name must contain only letters and spaces."
            )
        return value

    def validate_primary_mobile(self, value):
        try:
            validate_user_mobile(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        else:
            if CustomUser.objects.filter(primary_mobile=value).exists():
                raise serializers.ValidationError("Phone number is already in use.")
            return value


class SignupSerializer(BaseUserInputSerializer):
    pass


class FinalizeSignInSerializer(serializers.Serializer):

    primary_mobile = serializers.CharField(max_length=13, allow_blank=False)

    email = serializers.EmailField(
        max_length=255,
        allow_blank=False,
        help_text="Must be a valid email address",
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=40,
        help_text="At least 1 uppercase letter, 1 lowercase letter, 1 number, 1 special character",
    )

    def validate_primary_mobile(self, value):
        try:
            validate_user_mobile(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered")
        try:
            validate_user_email(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value

    def validate_password(self, value):
        try:
            validate_user_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def save(self, **kwargs):
        user = self.context["user"]
        user.email = self.validated_data["email"]
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["username", "email", "password"])
        return user


class OTPVerifyserializers(serializers.Serializer):
    primary_mobile = serializers.CharField(max_length=13, allow_blank=False)

    otp_code = serializers.CharField(
        min_length=6,
        max_length=6,
        allow_blank=False,
        validators=[
            RegexValidator(
                regex=r"^\d{6}$", message="OTP code must be exactly 6 digits"
            )
        ],
    )

    def validate_primary_mobile(self, value):
        try:
            validate_user_mobile(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        else:
            return value


class ResentOTPSerializers(serializers.Serializer):
    primary_mobile = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+20(10|11|12|15)\d{8}$",
                message="Phone number must be in the format +201XXXXXXXX (Egypt) ",
            )
        ]
    )


class LoginSerializer(serializers.Serializer):

    # phone, email, or username
    identifier = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255,
        help_text="Username, phone number, or email",
    )

    password = serializers.CharField(
        write_only=True,
        allow_blank=False,
        min_length=8,
        max_length=128,
    )

    remember_me = serializers.BooleanField(default=False)

    cf_turnstile_response = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        help_text="Cloudflare Turnstile token",
    )

    def get_user(self, identifier):
        if not identifier:
            return None

        user = CustomUser.objects.filter(
            Q(username=identifier) | Q(email=identifier) | Q(primary_mobile=identifier)
        ).first()
        return user

    def validate_identifier(self, value):
        # phone
        if value.startswith("+"):
            try:
                validate_user_mobile(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)
        # email
        elif "@" in value:
            try:
                validate_user_email(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)
        # username
        else:
            if len(value) < 3:
                raise serializers.ValidationError("Username is too short")
        return value

    def validate(self, attrs):
        identifier = attrs.get("identifier").strip()
        password = attrs.get("password")
        remember_me = attrs.get("remember_me", False)
        token = attrs.get("cf_turnstile_response", None)

        # 🔹 Step 1: Turnstile tekshiruvi
        from django.conf import settings

        if not getattr(settings, "TEST_MODE", False):
            if not token or not verify_turnstile(token):
                raise serializers.ValidationError("Invalid Turnstile token")

        try:
            user = self.get_user(identifier)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "Username/Phone/Email/Password is incorrect"
            )
        else:
            # 🔹 Step 3: Password validation
            if not user or not user.check_password(password):
                raise serializers.ValidationError(
                    "Username/Phone/Email/Password is incorrect"
                )

            attrs["user"] = user
            attrs["remember_me"] = remember_me
            return attrs


class RefreshTokenSerializers(serializers.Serializer):
    refresh = serializers.CharField(
        write_only=True,
        allow_blank=False,
        min_length=20,
        max_length=512,
        help_text="Valid refresh token",
    )


class Enable2FASerializer(serializers.Serializer):
    """
    No input fields required.
    Used only to enable 2FA for the current user.
    """

    def save(self, **kwargs):
        user = self.context["request"].user

        import pyotp, secrets

        user.is_2fa_enabled = True
        user.two_fa_secret = pyotp.random_base32()
        user.backup_codes = [secrets.token_hex(4) for _ in range(5)]

        user.save(update_fields=["is_2fa_enabled", "two_fa_secret", "backup_codes"])
        return user


class TwoFABackupVerifySerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    backup_code = serializers.CharField(max_length=100)


class TwoFACodeVerifySerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    code = serializers.CharField(max_length=10)
