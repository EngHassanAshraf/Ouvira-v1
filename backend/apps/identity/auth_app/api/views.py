import logging
from datetime import timedelta
from random import randint


from django.conf import settings
from django.db import IntegrityError, DataError, DatabaseError
from django.utils import timezone

from apps.identity.account.models.user import CustomUser, TwoALoginSession

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions, serializers, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import OTP, LoginActivity
from .serializers import (
    Enable2FASerializer,
    SignupSerializer,
    RefreshTokenSerializers,
    OTPVerifyserializers,
    ResentOTPSerializers,
    LoginSerializer,
    TwoFACodeVerifySerializer,
    TwoFABackupVerifySerializer,
    FinalizeSignInSerializer,
)

from apps.identity.account.services import UserService
from apps.shared.exceptions import BusinessException
from apps.shared.messages.error import ERROR_MESSAGES
from apps.shared.messages.success import SUCCESS_MESSAGES

from ..utilits import verify_turnstile


MAX_ATTEMPTS = 3
BLOCK_MINUTES = 15
OTP_EXPIRY_MINUTES = 60


# SIGNUP VIEW
class SignUPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signup"

    @swagger_auto_schema(request_body=SignupSerializer)
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data.get("primary_mobile")
        full_name = serializer.validated_data.get("full_name")

        if not phone_number or not full_name:
            return Response(
                {"status": "warning", "message": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user, created = CustomUser.objects.get_or_create(
                primary_mobile=phone_number,
                defaults={
                    "full_name": full_name,
                    "username": full_name.replace(" ", "_").lower()
                    + str(randint(1000, 9999)),
                },
            )

            OTP.objects.filter(phone_number=phone_number).delete()

            otp_code = str(randint(100000, 999999))
            expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

            OTP.objects.create(
                phone_number=phone_number, otp_code=otp_code, expires_at=expires_at
            )

            # success = send_sms(phone_number,f"Your OTP code is {otp_code}", settings.TWILIO_PHONE_NUMBER)
            return Response(
                {"status": "success", "message": SUCCESS_MESSAGES["PHONE_OTP_SENT"]},
                status=status.HTTP_200_OK,
            )
        except IntegrityError:
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["MOBILE_ALREADY_USED"]},
                status=status.HTTP_409_CONFLICT,
            )

        except ValidationError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except DatabaseError:
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception:
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# VERIFY OTP VIEW
logger = logging.getLogger(__name__)


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    @swagger_auto_schema(request_body=OTPVerifyserializers)
    def post(self, request):
        serializer = OTPVerifyserializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data.get("primary_mobile")
        otp_code = serializer.validated_data.get("otp_code")

        try:
            otp_entry = OTP.objects.filter(phone_number=phone_number).first()
            if not otp_entry:
                return Response(
                    {"status": "error", "message": ERROR_MESSAGES["OTP_EXPIRED"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if otp_entry.is_blocked:
                if otp_entry.blocked_until and otp_entry.blocked_until > timezone.now():
                    return Response(
                        {"status": "error", "message": ERROR_MESSAGES["OTP_EXPIRED"]},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                otp_entry.is_blocked = False
                otp_entry.attempts = 0
                otp_entry.blocked_until = None
                otp_entry.save()

            # Expiration check
            if otp_entry.expires_at < timezone.now():
                otp_entry.delete()
                return Response(
                    {"status": "error", "message": ERROR_MESSAGES["OTP_EXPIRED"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # OTP mismatch
            if otp_entry.otp_code != otp_code:
                otp_entry.attempts += 1

                if otp_entry.attempts >= MAX_ATTEMPTS:
                    otp_entry.is_blocked = True
                    otp_entry.blocked_until = timezone.now() + timedelta(
                        minutes=BLOCK_MINUTES
                    )

                otp_entry.save()

                return Response(
                    {"status": "error", "message": ERROR_MESSAGES["INCORRECT_OTP"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = CustomUser.objects.filter(primary_mobile=phone_number).first()
            if not user:
                return Response(
                    {"status": "error", "message": ERROR_MESSAGES["ACCOUNT_NOT_FOUND"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.phone_verified = True
            user.save()

            otp_entry.delete()

            return Response(
                {"status": "succes", "message": SUCCESS_MESSAGES["MOBILE_VALIDATED"]},
                status=status.HTTP_200_OK,
            )

        except DatabaseError as e:
            logger.exception("Database error during OTP verification")
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            logger.exception("Unexpected error during OTP verification")
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FinalizeSignInView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "finalize_signin"

    swagger_auto_schema(request_body=FinalizeSignInSerializer)

    def post(self, request):
        user_data = request.data
        primary_mobile = user_data.get("primary_mobile")
        print(user_data)
        serializer = FinalizeSignInSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserService.update_existing_user(**serializer.validated_data)
            print(user)

        except BusinessException as e:
            logger.warning(
                f"Business error during finalizing sign-in for {primary_mobile}: {e.message}"
            )
            return Response(
                {"status": "error", "message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            logger.warning(
                f"Validation error during finalizing sign-in for {primary_mobile}: {str(e)}"
            )
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PermissionError as e:
            logger.warning(
                f"Permission error during finalizing sign-in for {primary_mobile}: {str(e)}"
            )
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        except Exception as e:
            logger.exception("Unexpected error during finalizing sign-in")
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info(
            f"User with phone {primary_mobile} successfully finalized sign-in and assigned as owner."
        )
        return Response(
            {"status": "success", "message": SUCCESS_MESSAGES["ASSIGNED_AS_OWNER"]},
            status=status.HTTP_200_OK,
        )


class ResentOTPView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_resend"

    @swagger_auto_schema(request_body=ResentOTPSerializers, security=[])
    def post(self, request):
        token = request.data.get("cf-turnstile-response")
        if not token or not verify_turnstile(token, request.META.get("REMOTE_ADDR")):
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ResentOTPSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["primary_mobile"]

        # oxirgi otpni olish uchun
        user_exists = CustomUser.objects.filter(primary_mobile=phone_number).exists()
        if not user_exists:
            return Response(
                {"status": "error", "message": ERROR_MESSAGES["ACCOUNT_NOT_FOUND"]},
                status=status.HTTP_403_FORBIDDEN,
            )

        OTP.objects.filter(phone_number=phone_number).delete()

        # yangi otp yaratish uchun
        otp_code = str(randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

        OTP.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at,
            attempts=0,
            is_blocked=False,
            blocked_until=None,
        )

        return Response(
            {
                "status": "success",
                "message": SUCCESS_MESSAGES["PHONE_OTP_SENT"],
                "expiry": "5 minutes",
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            identifier = (
                request.data.get("primary_mobile")
                or request.data.get("username")
                or request.data.get("email")
            )
            user = serializer.get_user(identifier) if identifier else None
            print(user)
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.lock_account(minutes=30)
                else:
                    user.save(update_fields=["failed_login_attempts"])

            return Response(
                {"message": ERROR_MESSAGES["LOGIN_CREDENTIALS_INCORRECT"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        remember_me = serializer.validated_data["remember_me"]

        # 2FA YOQILGANMI? Shuni tekshiramiz
        if getattr(user, "is_2fa_enabled", False):
            session = TwoALoginSession.objects.create(user=user)

            # 🔹 Code generate qilish
            if user.two_fa_type == "AUTHENTICATOR":
                import pyotp

                totp = pyotp.TOTP(user.two_fa_secret)
                generated_code = totp.now()  # dev/testing uchun
            elif user.two_fa_type == "SMS":
                generated_code = str(randint(100000, 999999))
                # send_sms(user.primary_mobile, generated_code)  # Production-da

            LoginActivity.objects.create(
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return Response(
                {
                    "message": SUCCESS_MESSAGES.get(
                        "VERIFICATION_ACCEPTED", "2fa verification required"
                    ),
                    "2fa_required": True,
                    "session_id": str(session.session_id),
                    "generated_code": generated_code,  # faqat dev/testing
                },
                status=status.HTTP_200_OK,
            )

        # ================================
        # 🔓 2FA yoqilmagan → oddiy login ishlaydi
        # ================================
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        if remember_me:
            refresh.access_token.set_exp(lifetime=timedelta(days=14))

        LoginActivity.objects.create(
            user=user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response(
            {
                "message": SUCCESS_MESSAGES["LOGIN_SUCCESS"],
                "access": access_token,
                "refresh": refresh_token,
                "expires_in": 3600,
                "user_role": user.user_role,
                "2fa_required": False,
            },
            status=status.HTTP_200_OK,
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class LogouteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            if not refresh_token:
                return Response(
                    {"messge": ERROR_MESSAGES["SYSTEM_ERROR"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": SUCCESS_MESSAGES["LOGGED_OUT"]},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {"message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh"

    @swagger_auto_schema(request_body=RefreshTokenSerializers)
    def post(self, request):
        serializer = RefreshTokenSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            new_access = str(token.access_token)
            return Response(
                {"access": new_access, "expires_in": 3600}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"message": ERROR_MESSAGES["SYSTEM_ERROR"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Enable2FAView(generics.UpdateAPIView):
    serializer_class = Enable2FASerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "enable_2fa"

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(request_body=Enable2FASerializer)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"message": ERROR_MESSAGES["SYSTEM_ERROR"]}, status=400)
        serializer.save()

        return Response(
            {
                "message": SUCCESS_MESSAGES["VERIFICATION_ACCEPTED"],
                "backup_codes": serializer.instance.backup_codes,
            },
            status=200,
        )


class TwoFAVerifyBackupView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "twofa_verify"

    @swagger_auto_schema(request_body=TwoFABackupVerifySerializer)
    def post(self, request):
        serializer = TwoFABackupVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        backup_code = serializer.validated_data["backup_code"]

        try:
            session = TwoALoginSession.objects.get(
                session_id=session_id, is_verified=False
            )
        except TwoALoginSession.DoesNotExist:
            return Response(
                {"message": ERROR_MESSAGES["ACCOUNT_NOT_FOUND"]}, status=400
            )

        if session.is_expired():
            return Response({"message": ERROR_MESSAGES["OTP_EXPIRED"]}, status=400)

        user = session.user

        if backup_code not in user.backup_codes:
            return Response({"message": ERROR_MESSAGES["INCORRECT_OTP"]}, status=400)

        user.backup_codes.remove(backup_code)
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "expires_in": 3600,
                "message": SUCCESS_MESSAGES["VERIFICATION_ACCEPTED"],
            },
            status=200,
        )


class TwoFAVerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "twofa_verify"

    @swagger_auto_schema(request_body=TwoFACodeVerifySerializer, security=[])
    def post(self, request):
        serializer = TwoFACodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        code = serializer.validated_data["code"]

        # 🔹 Sessionni olish
        try:
            session = TwoALoginSession.objects.get(
                session_id=session_id, is_verified=False
            )
        except TwoALoginSession.DoesNotExist:
            return Response({"error": "Invalid or expired session"}, status=400)

        if session.is_expired():
            return Response({"error": "Expired session"}, status=400)

        user = session.user

        # 🔹 Code verify qilish
        if user.two_fa_type == "AUTHENTICATOR":
            import pyotp

            totp = pyotp.TOTP(user.two_fa_secret)
            if not totp.verify(code, valid_window=6):
                return Response({"error": "Invalid 2FA code"}, status=400)
        elif user.two_fa_type == "SMS":
            # TODO: SMS code tekshirish logikasi
            return Response(
                {"error": "SMS verification not implemented yet"}, status=400
            )

        # 🔹 Sessionni tasdiqlash
        session.is_verified = True
        session.save()

        # 🔹 Token yaratish
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "expires_in": 3600,
                "message": "Login successful",
            },
            status=200,
        )
