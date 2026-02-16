from django.urls import path

from .views import (
    SignUPView,
    OTPVerifyView,
    FinalizeSignInView,
    ResentOTPView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    Enable2FAView,
    TwoFAVerifyCodeView,
    TwoFAVerifyBackupView,
)

urlpatterns = [
    # Signup endpoints
    path("signup/", SignUPView.as_view(), name="signup"),
    path("finalize-signin/", FinalizeSignInView.as_view(), name="finalize-signin"),

    # OTP endpoints
    path("verify-otp/", OTPVerifyView.as_view(), name="verify-otp"),
    path("resent-otp/", ResentOTPView.as_view(), name="resent-otp"),

    # Authentication endpoints
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),

    # 2FA endpoints
    path("settings_enable-2fa/", Enable2FAView.as_view(), name="enable-2fa"),
    path("login-2fa-verify-code/", TwoFAVerifyCodeView.as_view(), name="2fa-verify-code"),
    path("login-2fa-verify-backup/", TwoFAVerifyBackupView.as_view(), name="2fa-verify-backup"),
]
