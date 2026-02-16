from django.contrib import admin

from .models import Company
from .models import CompanySettings

# from .models.invitation import CompanyInvitation
# from .models.membership import CompanyMembership


admin.site.register(Company)
admin.site.register(CompanySettings)
# admin.site.register(CompanyInvitation)
# admin.site.register(CompanyMembership)
