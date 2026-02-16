from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.identity.account.models import CustomUser
from apps.core.models import TimeStampedModel
from apps.company.models import Company


class Permission(TimeStampedModel):
    code = models.CharField(max_length=100, unique=True)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class Role(TimeStampedModel):
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.CASCADE, related_name="roles"
    )  # Null = System Role
    role = models.CharField(max_length=50)
    desc = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)

    class Meta:
        unique_together = ("company", "role")
        indexes = [
            models.Index(fields=["company", "role"]),
        ]

    def __str__(self):
        return f"{self.company} - {self.role}"


class RolePermission(TimeStampedModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    granted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("role", "permission")
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"

    def __str__(self) -> str:
        return f"{self.role} - {self.permission}"


class UserCompany(TimeStampedModel):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="companies"
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="users")

    is_primary_company = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "company")
        indexes = [
            models.Index(fields=["user", "company"]),
        ]
        verbose_name = "User Company"
        verbose_name_plural = "User Companies"

    def __str__(self) -> str:
        return f"{self.user} @ {self.company}"


class UserCompanyRole(TimeStampedModel):
    user_company = models.ForeignKey(
        UserCompany, on_delete=models.CASCADE, related_name="roles"
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_company", "role")
        verbose_name = "User Company Role"

    def __str__(self) -> str:
        return f"{self.user_company} | {self.role}"


class Invitation(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("expired", "Expired"),
        ("revoked", "Revoked"),
    )

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="invitations"
    )

    email = models.EmailField(db_index=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    token = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    expires_at = models.DateTimeField()

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
    )

    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invitations",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_invitations"
        verbose_name = _("Company Invitation")
        verbose_name_plural = _("Company Invitations")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"{self.email} → {self.company} ({self.status})"

    def is_expired(self):
        return self.expires_at < timezone.now()

    def mark_expired(self):
        if self.status == self.STATUS_CHOICES[0][0]:
            self.status = self.STATUS_CHOICES[2][0]
            self.save(update_fields=["status"])

    @classmethod
    def default_expiry(cls):
        return timezone.now() + timedelta(days=7)
