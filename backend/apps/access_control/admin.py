from django.contrib import admin
from .models import (
    Role,
    Permission,
    RolePermission,
    UserCompany,
    UserCompanyRole,
    Invitation,
)

admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserCompany)
admin.site.register(UserCompanyRole)
admin.site.register(Invitation)
