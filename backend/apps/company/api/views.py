from rest_framework.generics import CreateAPIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.company.models import Company, CompanySettings
from .serializers import CompanySerializer, CompanySettingsSerializer


class CompanyCreateView(CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class CompanySettingsAddView(CreateAPIView):
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer
    permission_classes = [IsAuthenticated]
