from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.models import AssignmentGroup
from apps.learning.serializers.v1 import AssignmentGroupRetrieveSerializer, AssignmentRelationListSerializer
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import AssignmentGroupTracker
from apps.my_learning.serializers.v1 import (
    UserAssignmentTrackerListSerializer,
    UserBaseLearningListSerializer,
    UserBaseLearningRetrieveModelSerializer,
)
from apps.my_learning.serializers.v1.tracker.assignment import UserAssignmentListModelSerializer


class UserAssignmentGroupListSerializer(UserBaseLearningListSerializer):
    """Serializer class to list the enrolled assignment details."""

    class Meta(UserBaseLearningListSerializer.Meta):
        model = AssignmentGroup
        fields = UserBaseLearningListSerializer.Meta.fields


class UserAssignmentGroupRetrieveSerializer(
    AssignmentGroupRetrieveSerializer, UserBaseLearningRetrieveModelSerializer
):
    """Serializer class to retrieve the enrolled assignment group details."""

    class Meta(AssignmentGroupRetrieveSerializer.Meta):
        fields = AssignmentGroupRetrieveSerializer.Meta.fields + [
            "enrolled_details",
            "tracker_detail",
            "is_feedback_given",
        ]


class UserAssignmentGroupTrackerCreateSerializer(AppCreateModelSerializer):
    """CUD Serializer class for the User assignment group."""

    class Meta(AppCreateModelSerializer.Meta):
        model = AssignmentGroupTracker
        fields = ["assignment_group", "enrollment"]

    def validate(self, attrs):
        """Validate if tracker is already present for the user with this assignment group."""

        enrollment_instance = attrs["enrollment"]
        user = self.get_user()
        if not enrollment_instance.is_enrolled:
            raise serializers.ValidationError({"enrollment": "Admin approval is pending."})
        if enrollment_instance.user != user and enrollment_instance.user_group not in user.related_user_groups.all():
            raise serializers.ValidationError({"enrollment": "Detail not found."})
        if user.related_assignment_group_trackers.filter(assignment_group=attrs["assignment_group"]).first():
            raise serializers.ValidationError({"assignment_group": "Already started."})
        return attrs

    def create(self, validated_data):
        """Overridden to handle enrollment, progress start/stop."""

        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        return instance


class UserAssignmentRelationListSerializer(AssignmentRelationListSerializer):
    """Serializer class to list the assignment relation list with tracker details."""

    tracker_detail = serializers.SerializerMethodField()
    assignment = UserAssignmentListModelSerializer(read_only=True)

    def get_tracker_detail(self, obj):
        """Returns the assignment tracker data."""

        user = self.context.get("request").user
        tracker_instance = obj.assignment.related_assignment_trackers.filter(user=user).first()
        return UserAssignmentTrackerListSerializer(tracker_instance).data if tracker_instance else None

    class Meta(AssignmentRelationListSerializer.Meta):
        fields = AssignmentRelationListSerializer.Meta.fields + [
            "tracker_detail",
        ]


class UserAssignmentGroupTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list assignment group trackers."""

    assignment_group = BaseIDNameSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = AssignmentGroupTracker
        fields = [
            "id",
            "assignment_group",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "completion_date",
            "ccms_id",
            "allowed_attempt",
            "available_attempt",
            "is_pass",
            "is_ccms_obj",
        ]
