# import uuid
# from datetime import timedelta

# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from .company import Company


# class CompanyInvitation(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "pending", _("Pending")
#         ACCEPTED = "accepted", _("Accepted")
#         EXPIRED = "expired", _("Expired")
#         CANCELED = "canceled", _("Canceled")

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name="invitations",
#         verbose_name=_("Company"),
#     )

#     email = models.EmailField(verbose_name=_("Invited email"))

#     role = models.CharField(
#         max_length=20,
#         choices=(("admin", "Admin"), ("hr", "HR Manager"), ("user", "User")),
#         default="user",
#         verbose_name=_("Role"),
#     )

#     token = models.UUIDField(
#         default=uuid.uuid4,
#         unique=True,
#         editable=False,
#         verbose_name=_("Invitation Token"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#         verbose_name=_("Status"),
#     )

#     expires_at = models.DateTimeField(
#         verbose_name=_("Expires at"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Created at"),
#     )

#     class Meta:
#         db_table = "company_invitations"
#         verbose_name = _("Company Invitation")
#         verbose_name_plural = _("Company Invitations")
#         indexes = [
#             models.Index(fields=["email"]),
#             models.Index(fields=["token"]),
#         ]

#     def __str__(self):
#         return f"{self.email} → {self.company} ({self.status})"

#     # 🔒 Domain helpers (logic emas, holat tekshirish)
#     def is_expired(self) -> bool:
#         return timezone.now() >= self.expires_at

#     def mark_expired(self):
#         if self.status == self.Status.PENDING:
#             self.status = self.Status.EXPIRED
#             self.save(update_fields=["status"])

#     @classmethod
#     def default_expiry(cls):
#         return timezone.now() + timedelta(days=7)
