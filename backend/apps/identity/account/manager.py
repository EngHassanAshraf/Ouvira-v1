from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def __init__(self) -> None:
        super().__init__()

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_with_role(self, **extra_fields):
        if self.model.objects.count() == 0:
            extra_fields["user_role"] = "account_owner"
        else:
            extra_fields.setdefault("user_role", "employee")

        password = extra_fields.pop("password", None)
        username = extra_fields.get("username")

        return self.create_user(username=username, password=password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("user_role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(username=username, password=password, **extra_fields)
