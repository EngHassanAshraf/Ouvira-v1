from rest_framework.exceptions import PermissionDenied
from .models.user import CustomUser, RoleChangeLog
from apps.shared.exceptions import BusinessException
from apps.shared.messages.error import ERROR_MESSAGES
from django.shortcuts import get_object_or_404


class UserService:

    @staticmethod
    def update_existing_user(**data):
        """
        OTP orqali yaratilgan userni topib update qiladi.
        Agar topilmasa, xatolik beradi.
        """
        print(data)
        primary_mobile = data.get("primary_mobile")
        print(primary_mobile)
        user = CustomUser.objects.filter(primary_mobile=primary_mobile).first()

        if not user:
            raise BusinessException(ERROR_MESSAGES["ACCOUNT_NOT_FOUND"])

        password = data.pop("password", None)

        # Mavjud userni update qilish (final signup)
        for key, value in data.items():
            setattr(user, key, value)

        if password:
            user.set_password(password)
        user.save()

        return user


class RoleService:
    ROLE_HIERARCHY = {"account_owner": 4, "admin": 3, "manager": 2, "employee": 1}

    @classmethod
    def change_user_role(cls, register_user, target_user, new_role):
        target_user = get_object_or_404(CustomUser, id=target_user)

        if new_role not in cls.ROLE_HIERARCHY:
            raise ValueError("Unrecognized Error or Invalid role specified.")

        if cls.ROLE_HIERARCHY.get(register_user.user_role, 0) <= cls.ROLE_HIERARCHY.get(
            target_user.user_role, 0
        ):
            raise PermissionDenied("You cannot change this user's role.")

        if cls.ROLE_HIERARCHY.get(register_user.user_role, 0) <= cls.ROLE_HIERARCHY.get(
            new_role, 0
        ):
            raise PermissionDenied("You can't give this role away.")

        old_role = target_user.user_role
        target_user.user_role = new_role
        target_user.save()

        RoleChangeLog.objects.create(
            user=target_user,
            old_role=old_role,
            new_role=new_role,
            changed_by=register_user,
        )

        return target_user
