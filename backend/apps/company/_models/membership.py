# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .company import Company


# class CompanyMembership(models.Model):
#     class Role(models.TextChoices):
#         OWNER = "owner", _("Owner")
#         ADMIN = "admin", _("Admin")
#         HR = "hr", _("HR Manger")
#         USER = "user", _("User")

#     class Status(models.TextChoices):
#         ACTIVE = "active", _("Active")
#         REMOVED = "removed", _("Removed")

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name="memberships",
#         verbose_name=_("Company"),
#     )
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="company_memberships",
#         verbose_name=_("User"),
#     )
#     role = models.CharField(
#         max_length=20,
#         choices=Role.choices,
#         default=Role.USER,
#         verbose_name=_("Role")
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.ACTIVE,
#         verbose_name=_("Status")
#     )
#     joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Joined at"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

#     class Meta:
#         db_table = "company_memberships"
#         verbose_name = _("Company membership")
#         verbose_name_plural = ("Company memberships")
#         ordering = ["-joined_at"]

#     def __str__(self):
#         return f"{self.user} {self.company} ({self.role})"

#     def is_owner(self) -> bool:
#         return self.role == self.Role.OWNER

#     def is_admin(self) -> bool:
# return self.role in {self.Role.OWNER, self.Role.ADMIN}
