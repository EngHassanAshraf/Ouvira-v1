import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta

load_dotenv()


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


BASE_DIR = Path(__file__).resolve().parent.parent

TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY")

TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

TEST_MODE = os.getenv("TEST_MODE", "False") == "True"


# Application definition

DEFAULT_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
)

SHARED_THIRD_PARTY = ("django_tenants", "corsheaders")

SHARED_CREATED_APPS = ("apps.identity.account", "apps.tenant")

SHARED_APPS = [*DEFAULT_APPS, *SHARED_THIRD_PARTY, *SHARED_CREATED_APPS]

TENANT_CREATED_APPS = (
    "apps.core",
    "apps.audit",
    "apps.access_control",
    "apps.company",
    # "apps.entrprise_service.organization",
    "apps.identity.auth_app",
)


TENANT_THIRD_PARTY = (
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
)


TENANT_APPS = [*TENANT_THIRD_PARTY, *TENANT_CREATED_APPS]


INSTALLED_APPS = [app for app in TENANT_APPS if app not in SHARED_APPS] + list(
    SHARED_APPS
)

AUTH_USER_MODEL = "account.CustomUser"

TENANT_MODEL = "tenant.Tenant"
TENANT_DOMAIN_MODEL = "tenant.Domain"
TENANT_BASE_DOMAIN = os.getenv("TENANT_BASE_DOMAIN", "")

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "200/d",
        "user": "1000/d",
        "signup": "3/h",
        "finalize_signin": "3/h",
        "login": "5/m",
        "otp_resend": "3/h",
        "otp_verify": "5/m",
        "twofa_verify": "5/m",
        "refresh": "20/m",
        "enable_2fa": "10/h",
        "register_owner": "3/h",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

SESSION_COOKIE_AGE = 30 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

MIDDLEWARE = [
    "apps.tenant.middleware.HeaderTenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

APPEND_SLASH = os.getenv("DJANGO_APPEND_SLASH", "True") == "True"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

CORS_ALLOW_ALL_ORIGINS = DEBUG

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": True,  # JWT ishlatamiz, session auth kerak emas
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token kiriting: Bearer <token>",
        }
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Cairo"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
