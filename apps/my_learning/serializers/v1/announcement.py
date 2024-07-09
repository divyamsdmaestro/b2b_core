from rest_framework import serializers

from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSpecificImageFieldSerializer,
    AppWriteOnlyModelSerializer,
)
from apps.my_learning.config import AnnouncementTypeChoices
from apps.my_learning.models import Announcement


class AnnouncementCUDModelSerializer(AppWriteOnlyModelSerializer):
    """CUD Serializer for `Announcement` model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Announcement
        fields = [
            "title",
            "announcement_image",
            "type",
            "user",
            "user_group",
            "text",
        ]

    def validate(self, attrs):
        """Overriden to validate the corresponding fields present or not."""

        if not attrs["title"]:
            raise serializers.ValidationError({"title": "This field is required"})
        if not attrs["text"]:
            raise serializers.ValidationError({"text": "This field is required"})
        if attrs["type"] == AnnouncementTypeChoices.user_level and not attrs["user"]:
            raise serializers.ValidationError({"user": "This field is required"})
        elif attrs["type"] == AnnouncementTypeChoices.user_group_level and not attrs["user_group"]:
            raise serializers.ValidationError({"user_group": "This field is required"})
        return attrs

    def get_meta(self) -> dict:
        """get meta data."""

        return {
            "type": self.serialize_dj_choices(AnnouncementTypeChoices.choices),
        }


class AnnouncementListModelSerializer(AppReadOnlyModelSerializer):
    """List Serializer for `Announcement` model."""

    announcement_image = AppSpecificImageFieldSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Announcement
        fields = [
            "id",
            "title",
            "announcement_image",
            "type",
            "user",
            "user_group",
            "text",
            "created_at",
            "modified_at",
        ]
