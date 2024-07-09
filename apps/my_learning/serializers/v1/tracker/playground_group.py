from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer
from apps.learning.models import PlaygroundGroup
from apps.learning.serializers.v1 import PlaygroundRelationModelRetrieveSerializer
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import UserPlaygroundGroupTracker
from apps.my_learning.serializers.v1 import (
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
    UserPlaygroundTrackerListSerializer,
)
from apps.my_learning.tasks import PlaygroundGroupEnrollmentTask
from apps.tenant_service.middlewares import get_current_db_name


class UserPlaygroundGroupListSerializer(UserBaseLearningCertificateListSerializer):
    """Serializer class to retrieve the enrolled playground details."""

    class Meta(UserBaseLearningCertificateListSerializer.Meta):
        model = PlaygroundGroup
        fields = UserBaseLearningCertificateListSerializer.Meta.fields


class UserPlaygroundGroupRetrieveSerializer(UserBaseLearningRetrieveModelSerializer):
    """Serializer class to retrieve the enrolled playground details."""

    class Meta(UserBaseLearningRetrieveModelSerializer.Meta):
        model = PlaygroundGroup
        fields = UserBaseLearningRetrieveModelSerializer.Meta.fields


class UserPlaygroundGroupTrackerCreateSerializer(AppCreateModelSerializer):
    """CUD Serializer class for the User playground group."""

    class Meta(AppCreateModelSerializer.Meta):
        model = UserPlaygroundGroupTracker
        fields = ["playground_group", "enrollment"]

    def validate(self, attrs):
        """Validate if tracker is already present for the user with this playground group."""

        enrollment_instance = attrs["enrollment"]
        if (
            enrollment_instance.user != self.get_user()
            and enrollment_instance.user_group not in self.get_user().related_user_groups.all()
        ):
            raise serializers.ValidationError({"enrollment": "Detail not found."})
        if not enrollment_instance.is_enrolled:
            raise serializers.ValidationError({"enrollment": "Admin approval is pending."})
        if (
            self.get_user()
            .related_user_playground_group_trackers.filter(playground_group=attrs["playground_group"])
            .first()
        ):
            raise serializers.ValidationError({"enrollment": "Already started."})
        return attrs

    def create(self, validated_data):
        """Overridden to handle enrollment, progress start/stop."""

        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        PlaygroundGroupEnrollmentTask().run_task(tracker_id=instance.id, db_name=get_current_db_name())
        return instance


class UserPlaygroundRelationListSerializer(PlaygroundRelationModelRetrieveSerializer):
    """Serializer class to list the playground relation list with tracker details."""

    tracker_detail = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the playground tracker data."""

        user = self.context.get("request").user
        tracker_instance = obj.playground.related_user_playground_trackers.filter(user=user).first()
        return UserPlaygroundTrackerListSerializer(tracker_instance).data if tracker_instance else None

    class Meta(PlaygroundRelationModelRetrieveSerializer.Meta):
        fields = PlaygroundRelationModelRetrieveSerializer.Meta.fields + [
            "tracker_detail",
        ]


class UserPlaygroundGroupTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list lp trackers."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserPlaygroundGroupTracker
        fields = [
            "id",
            "playground_group",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "completion_date",
        ]
