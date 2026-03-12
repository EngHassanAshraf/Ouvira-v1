import logging
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import BadHeaderError


logger = logging.getLogger(__name__)


def send_email(subject: str, message: str, recipient_email: str) -> bool:
    """
    Generic email sending service.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False
        )

        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except BadHeaderError:
        logger.error("Invalid header found while sending email.")
        return False

def send_password_reset_email(email: str, reset_link: str) -> bool:
    """
    Sent password reset email
    """
    subject = "Password Reset Request"
    message = f"Click the link bellow to reset your password:\n\n{reset_link}"

    return send_email(subject, message, email)

def send_notifiation_email(email:str, notification_message:str) -> bool:
    """
    Send sysytem notification email
    """
    subject = "Notification"
    message = notification_message

    return send_email(subject, message, email)


