import re
from rest_framework.exceptions import ValidationError


def validate_user_password(password):
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


def validate_user_email(email):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise ValidationError("Invalid email format.")
    if email.endswith("@example.com"):
        raise ValidationError("Email domain cannot be example.com.")
    if email.endswith("@test.com"):
        raise ValidationError("Email domain cannot be test.com.")
    if email.endswith("@invalid.com"):
        raise ValidationError("Email domain cannot be invalid.com.")
    if email.endswith("@fake.com"):
        raise ValidationError("Email domain cannot be fake.com.")


def validate_user_mobile(mobile):
    eg_mobile_regex = r"^\+20(10|11|12|15)\d{8}$"
    ksa_mobile_regex = r"^\+9665\d{8}$"

    if not re.match(eg_mobile_regex, mobile):
        if not re.match(ksa_mobile_regex, mobile):
            raise ValidationError(
                "Invalid Phone number format, correct formate should be '+CounteryCodeXXXXXXXXX'"
            )
