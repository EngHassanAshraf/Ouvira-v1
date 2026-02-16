from rest_framework.exceptions import PermissionDenied
from .models.user import CustomUser
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

        for key, value in data.items():
            setattr(user, key, value)

        if password:
            user.set_password(password)
        user.save()

        return user
