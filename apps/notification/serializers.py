from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer
from apps.notification.models import Notification


class NotificationListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `Notification` model."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "uuid",
            "user",
            "message",
            "is_read",
            "read_at",
            "created_at",
            "modified_at",
        ]


class NotificationBulkUpdateSerializer(AppSerializer):
    """Serializer class for Bulk-update of Notifications."""

    notifications = serializers.PrimaryKeyRelatedField(queryset=Notification.objects.all(), many=True)

    def validate(self, attrs):
        """Validate if notifications is of logged in user's."""

        request = self.context["request"]
        raw_notification_ids = request.data["notifications"]
        notification_obj = Notification.objects.filter(id__in=raw_notification_ids)
        if notification_obj.exclude(user=self.get_user()).exists():
            raise serializers.ValidationError({"notifications": "Invalid Notification ID's."})
        attrs["notification_objs"] = notification_obj
        return attrs
