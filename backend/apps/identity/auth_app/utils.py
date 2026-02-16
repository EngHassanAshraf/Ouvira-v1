"""
Utility functions for authentication app
"""
import re
import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


# ==================== VALIDATION FUNCTIONS ====================

def validate_user_password(password: str) -> None:
    """
    Validate password strength.
    
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(password) < 8 or len(password) > 40:
        raise ValidationError("Password length must be 8–40 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one Uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            "Password must contain at least one special character _, @, !, *, #, $."
        )


def validate_user_email(email: str) -> None:
    """
    Validate email format.
    
    Raises:
        ValidationError: If email format is invalid
    """
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise ValidationError("Invalid email format.")
    
    # Block common test/invalid domains
    blocked_domains = ["@example.com", "@test.com", "@invalid.com", "@fake.com"]
    for domain in blocked_domains:
        if email.endswith(domain):
            raise ValidationError(f"Email domain cannot be {domain}.")


def validate_user_mobile(mobile: str) -> None:
    """
    Validate mobile phone number format.
    Supports Egypt (+20) and Saudi Arabia (+966) formats.
    
    Raises:
        ValidationError: If mobile format is invalid
    """
    eg_mobile_regex = r"^\+20(10|11|12|15)\d{8}$"
    ksa_mobile_regex = r"^\+9665\d{8}$"

    if not re.match(eg_mobile_regex, mobile):
        if not re.match(ksa_mobile_regex, mobile):
            raise ValidationError(
                "Invalid Phone number format, correct format should be '+CountryCodeXXXXXXXXX'"
            )


# ==================== TURNSTILE VERIFICATION ====================

def verify_turnstile(token: str, remote_ip: str = None) -> bool:
    """
    Verify Cloudflare Turnstile token.
    
    Args:
        token: Turnstile response token
        remote_ip: Optional remote IP address
        
    Returns:
        True if token is valid, False otherwise
    """
    # Skip verification in test mode
    if getattr(settings, "TEST_MODE", True):
        return True
    
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }
    
    if remote_ip:
        data["remoteip"] = remote_ip

    try:
        resp = requests.post(url, data=data, timeout=5)
        result = resp.json()
        return result.get("success", False)
    except Exception:
        # Return False on any error
        return False
