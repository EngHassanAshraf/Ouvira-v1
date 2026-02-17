"""
Audit views — notifications, activity logs, and security audit logs.
"""
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)

from ..services import NotificationService, ActivityLogService, SecurityAuditLogService
from .serializers import (
    NotificationListSerializer,
    ActivityLogListSerializer,
    ActivityLogSerializer,
    SecurityAuditLogSerializer,
)
from apps.access_control.permissions.IsAdminUser import IsAdminUser


# ==================== NOTIFICATION VIEWS ====================

class NotificationListView(ListAPIView):
    """
    GET /notifications/ → list notifications for the authenticated user.
    Supports ?unread=true query param to filter unread only.
    """
    serializer_class = NotificationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = NotificationService.get_user_notifications(self.request.user)
        unread_only = self.request.query_params.get("unread")
        if unread_only and unread_only.lower() == "true":
            qs = qs.filter(read=False)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "unread_count": NotificationService.get_unread_count(request.user),
            "results": response.data,
        }
        return response


class NotificationMarkReadView(APIView):
    """
    POST /notifications/mark-read/
    Body: {"notification_id": <id>} — mark single notification as read
    Body: {"all": true} — mark all as read
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mark_all = request.data.get("all", False)
        notification_id = request.data.get("notification_id")

        if mark_all:
            count = NotificationService.mark_all_read(request.user)
            return Response(
                {"detail": f"Marked {count} notifications as read."},
                status=HTTP_200_OK,
            )

        if notification_id:
            try:
                NotificationService.mark_as_read(notification_id, request.user)
                return Response(
                    {"detail": "Notification marked as read."},
                    status=HTTP_200_OK,
                )
            except Exception:
                return Response(
                    {"detail": "Notification not found."},
                    status=HTTP_404_NOT_FOUND,
                )

        return Response(
            {"detail": "Provide 'notification_id' or 'all': true."},
            status=HTTP_200_OK,
        )


# ==================== ACTIVITY LOG VIEWS ====================

class ActivityLogListView(ListAPIView):
    """
    GET /activity-logs/?company=<id> → list activity logs for a company (admin only).
    """
    serializer_class = ActivityLogListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        company_id = self.request.query_params.get("company")
        if company_id:
            return ActivityLogService.get_activity_logs_for_company(int(company_id))
        return ActivityLogService.get_activity_logs_for_user(self.request.user)


class ActivityLogDetailView(ListAPIView):
    """
    GET /activity-logs/my/ → user's own activity logs.
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ActivityLogService.get_activity_logs_for_user(self.request.user)


# ==================== SECURITY AUDIT LOG VIEWS ====================

class SecurityAuditLogListView(ListAPIView):
    """
    GET /security-logs/ → user's own security audit logs.
    """
    serializer_class = SecurityAuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SecurityAuditLogService.get_logs_for_user(self.request.user)
