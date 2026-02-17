"""
Audit signals — log login/logout/signup events.

NOTE: The current ActivityLog model requires company + date FK,
so we only use NotificationService for signals that don't have
a company context. Activity logging should be done at the view/service
layer where company context is available.
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .services.notification_service import NotificationService

User = get_user_model()


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    """Log successful login activity."""
    # Activity logging requires company context — handled at view layer.
    # Signal only used for notification use cases if needed.
    pass


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Log logout activity."""
    pass


@receiver(post_save, sender=User)
def log_signup(sender, instance, created, **kwargs):
    """Notify new users upon signup."""
    if created:
        NotificationService.create_notification(
            user=instance,
            message="Welcome! You have successfully registered.",
        )
