from django.urls import path
from .views import (
    SignUPView,
    OTPVerifyView,
    FinalizeSignInView,
    ResentOTPView,
    LoginView,
    RefreshTokenView,
    LogouteView,
    Enable2FAView,
    TwoFAVerifyCodeView,
    TwoFAVerifyBackupView,
)

urlpatterns = [
    path("signup/", SignUPView.as_view(), name="signup"),
    path("verify-otp/", OTPVerifyView.as_view(), name="verify-otp"),
    path("finalize-singin/", FinalizeSignInView.as_view(), name="finalize-singin"),
    path("resent-otp/", ResentOTPView.as_view(), name="resent-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogouteView.as_view(), name="logoute"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path(
        "login-2fa-verify-backup/",
        TwoFAVerifyBackupView.as_view(),
        name="2fa-verify-backup",
    ),
    path(
        "login-2fa-verify-code/", TwoFAVerifyCodeView.as_view(), name="2fa-verify-code"
    ),
    path("settings_enable-2fa/", Enable2FAView.as_view(), name="enable-2fa"),
]
