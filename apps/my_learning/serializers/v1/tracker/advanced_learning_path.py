from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer
from apps.learning.config import LearningTypeChoices
from apps.learning.models import AdvancedLearningPath
from apps.learning.serializers.v1 import ALPLearningPathListModelSerializer
from apps.my_learning.models import UserALPTracker
from apps.my_learning.serializers.v1 import (
    BaseEnrollmentTrackerCreateSerializer,
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
    UserLearningPathListSerializer,
    UserLearningPathTrackerListSerializer,
)


class UserAdvancedLearningPathListSerializer(UserBaseLearningCertificateListSerializer):
    """Serializer class to list the alp with enrollment_details."""

    class Meta(UserBaseLearningCertificateListSerializer.Meta):
        model = AdvancedLearningPath
        fields = UserBaseLearningCertificateListSerializer.Meta.fields + [
            "no_of_lp",
        ]

    def get_filter_meta(self):
        """Return the filter meta."""

        data = super().get_filter_meta()
        data["learning_type"] = self.serialize_dj_choices(LearningTypeChoices.choices)
        return data


class UserAdvancedLearningPathRetrieveModelSerializer(UserBaseLearningRetrieveModelSerializer):
    """Serializer class to retrieve the advanced learning path."""

    class Meta(UserBaseLearningRetrieveModelSerializer.Meta):
        model = AdvancedLearningPath
        fields = UserBaseLearningRetrieveModelSerializer.Meta.fields + [
            "no_of_lp",
        ]


class UserALPTrackerCreateModelSerializer(BaseEnrollmentTrackerCreateSerializer):
    """Serializer class to add advanced_learning_path tracker."""

    class Meta(BaseEnrollmentTrackerCreateSerializer.Meta):
        model = UserALPTracker
        fields = BaseEnrollmentTrackerCreateSerializer.Meta.fields + [
            "advanced_learning_path",
        ]


class UserALPLearningPathListSerializer(ALPLearningPathListModelSerializer):
    """Serializer class to list the learning_path list with enrollment details."""

    tracker_detail = serializers.SerializerMethodField()
    learning_path = UserLearningPathListSerializer(read_only=True)
    is_start_hidden = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns learning_path enrolled details."""

        user = self.context.get("request").user
        lp_tracker_instance = obj.learning_path.related_user_learning_path_trackers.filter(user=user).first()
        if lp_tracker_instance:
            self.context["is_tracker_exists"] = True
            return UserLearningPathTrackerListSerializer(lp_tracker_instance).data
        else:
            self.context["is_tracker_exists"] = False
            return None

    def get_is_start_hidden(self, obj):
        """Returns True if the content is locked."""

        alp = obj.advanced_learning_path
        if not alp.is_dependencies_sequential or self.context["is_tracker_exists"]:
            return False
        previous_alp_lp_objs = alp.related_alp_learning_paths.filter(sequence__lt=obj.sequence).values_list(
            "learning_path_id", flat=True
        )
        if not previous_alp_lp_objs.exists():
            return False
        user = self.get_user()
        user_lp_tracker_qs = user.related_user_learning_path_trackers.filter(learning_path_id__in=previous_alp_lp_objs)
        if user_lp_tracker_qs.count() != previous_alp_lp_objs.count() or user_lp_tracker_qs.filter(is_completed=False):
            return True
        return False

    class Meta(ALPLearningPathListModelSerializer.Meta):
        fields = ALPLearningPathListModelSerializer.Meta.fields + [
            "tracker_detail",
            "is_start_hidden",
        ]


class UserALPTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list advanced learning path trackers."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserALPTracker
        fields = [
            "id",
            "advanced_learning_path",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "completion_date",
        ]
