from django.utils import timezone

from apps.common.views.api import AppModelListAPIViewSet
from apps.common.views.api.base import AppAPIView, LoggedInUserMixin
from apps.notification.models import Notification
from apps.notification.serializers import NotificationBulkUpdateSerializer, NotificationListSerializer


class NotificationListApiViewSet(LoggedInUserMixin, AppModelListAPIViewSet):
    """Api Viewset to list Notification."""

    queryset = Notification.objects.all().order_by("is_read", "-created_at")
    serializer_class = NotificationListSerializer
    search_fields = ["is_read"]
    filterset_fields = ["is_read"]

    def list(self, request, *args, **kwargs):
        """Include unread message count for the user."""

        response = super().list(request, *args, **kwargs)
        response.data["unread_message_count"] = self.get_queryset().unread().count()
        return response


class NotificationUpdateApiView(AppAPIView):
    """Api viewset to bulk update `Notification`."""

    serializer_class = NotificationBulkUpdateSerializer

    def post(self, request, *args, **kwargs):
        """Update LeaderboardCompetition for the current user."""

        serializer = self.get_valid_serializer()
        notifications = serializer.validated_data["notification_objs"]
        notifications.update(is_read=True, read_at=timezone.now())
        return self.send_response(data={"message": "Notification status updated successfully."})
