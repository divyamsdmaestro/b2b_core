from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer, AppSpecificImageFieldSerializer
from apps.learning.models import Course
from apps.my_learning.config import LearningStatusChoices


class T1UserTopCourseSerializer(AppSerializer):
    """Serializer class for T1 to get top 5 user courses."""

    tenant_id = serializers.CharField()
    user_id = serializers.CharField()


class T1CourseListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for Common Learnings."""

    image = AppSpecificImageFieldSerializer()
    skill = serializers.SerializerMethodField(read_only=True)

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Course
        fields = ["id", "uuid", "name", "proficiency", "image", "category", "skill"]


class T1UserCourseListSerializer(T1CourseListSerializer):
    """Serializer class for Common Learnings."""

    tracker_details = serializers.SerializerMethodField(read_only=True)

    def get_tracker_details(self, obj):
        """Returns the user tracker details."""

        tracker = self.context["course_trackers"].filter(course=obj).first()
        if tracker:
            return {
                "started_date": tracker.created_at,
                "completion_date": tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if tracker.is_completed
                else LearningStatusChoices.started,
                "learning_progress": tracker.progress,
            }
        else:
            return {
                "started_date": None,
                "completion_date": None,
                "learning_status": LearningStatusChoices.not_started,
                "learning_progress": None,
            }

    class Meta(T1CourseListSerializer.Meta):
        fields = T1CourseListSerializer.Meta.fields + ["tracker_details"]
