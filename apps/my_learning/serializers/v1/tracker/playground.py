from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.models import Playground
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import UserPlaygroundTracker
from apps.my_learning.serializers.v1 import (
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
)
from apps.my_learning.tasks import PlaygroundTrackingTask
from apps.tenant_service.middlewares import get_current_db_name


class UserPlaygroundListSerializer(UserBaseLearningCertificateListSerializer):
    """Serializer class to retrieve the enrolled playground details."""

    class Meta(UserBaseLearningCertificateListSerializer.Meta):
        model = Playground
        fields = UserBaseLearningCertificateListSerializer.Meta.fields + [
            "playground_type",
            "guidance_type",
            "tool",
        ]


class UserPlaygroundRetrieveSerializer(UserBaseLearningRetrieveModelSerializer):
    """Serializer class to retrieve the enrolled playground details."""

    class Meta(UserBaseLearningRetrieveModelSerializer.Meta):
        model = Playground
        fields = UserBaseLearningRetrieveModelSerializer.Meta.fields + [
            "playground_type",
            "guidance_type",
            "tool",
        ]


class UserPlaygroundTrackerCreateSerializer(AppWriteOnlyModelSerializer):
    """CUD Serializer class for the User playground."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserPlaygroundTracker
        fields = ["playground", "enrollment"]

    def validate(self, attrs):
        """Validate if tracker is already present for the user with this playground."""

        enrollment_instance = attrs["enrollment"]
        if (
            enrollment_instance.user != self.get_user()
            and enrollment_instance.user_group not in self.get_user().related_user_groups.all()
        ):
            raise serializers.ValidationError({"enrollment": "Detail not found."})
        if not enrollment_instance.is_enrolled:
            raise serializers.ValidationError({"enrollment": "Admin approval is pending."})
        if self.get_user().related_user_playground_trackers.filter(playground=attrs["playground"]).first():
            raise serializers.ValidationError({"enrollment": "Already started."})
        return attrs

    def create(self, validated_data):
        """Overridden to add necessary fields for PlaygroundTrackingModel dependent on Playground."""

        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        PlaygroundTrackingTask().run_task(tracker_id=instance.id, db_name=get_current_db_name())
        return instance


class UserPlaygroundTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list lp trackers."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserPlaygroundTracker
        fields = [
            "id",
            "playground",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "completion_date",
        ]
