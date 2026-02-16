from django.db import models
from django.utils import timezone
from django.conf import settings


class LoginActivity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="logn_activities",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} logged in at {self.timestamp}"

    class Meta:
        verbose_name = "Login Activity"
        verbose_name_plural = "Login Activities"


class OTP(models.Model):
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_currently_blocked(self):
        if self.is_blocked and self.blocked_until:
            return timezone.now() < self.blocked_until
        return False

    def __str__(self):
        return f"{self.phone_number} | {self.otp_code}"

    class Meta:
        indexes = [
            models.Index(fields=["phone_number"]),
        ]
        ordering = ["-created_at"]
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"


class PasswordHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_history",
    )

    password_hash = models.CharField(max_length=255)
    changed_via = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Password History"
        verbose_name_plural = "Passwords Histories"
