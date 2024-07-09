from django.db.models import Q
from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer
from apps.learning.config import AssessmentTypeChoices
from apps.learning.models import LPAssessment
from apps.learning.serializers.v1 import LPAssessmentListModelSerializer
from apps.my_learning.models import LPAssessmentTracker, LPAYakshaResult, LPAYakshaSchedule
from apps.my_learning.serializers.v1 import (
    BaseAssessmentTrackerListSerializer,
    BaseYakshaAssessmentResultListSerializer,
    BaseYakshaAssessmentScheduleListSerializer,
)


class LPATrackerListSerializer(BaseAssessmentTrackerListSerializer):
    """Course assessment tracker list serializer."""

    class Meta(BaseAssessmentTrackerListSerializer.Meta):
        model = LPAssessmentTracker
        fields = [
            "assessment",
            "user",
        ] + BaseAssessmentTrackerListSerializer.Meta.fields


# TODO: Need to change these lines
class LPATrackerCreateSerializer(AppCreateModelSerializer):
    """Serializer class to create a learning path assessments."""

    class Meta(AppCreateModelSerializer.Meta):
        model = LPAssessmentTracker
        fields = [
            "assessment",
            "ccms_id",
            "is_ccms_obj",
        ]

    def validate(self, attrs):
        """Validate the assessment is valid or not."""

        user = self.get_user()
        if attrs["is_ccms_obj"]:
            attrs["assessment"] = None
            if not attrs["ccms_id"]:
                raise serializers.ValidationError({"ccms_id": "This field is required."})
            if user.related_lp_assessment_trackers.filter(ccms_id=attrs["ccms_id"]).first():
                raise serializers.ValidationError({"ccms_id": "Already started."})
        else:
            attrs["ccms_id"] = None
            if not attrs["assessment"]:
                raise serializers.ValidationError({"assessment": "This field is required."})
            if user.related_lp_assessment_trackers.filter(assessment=attrs["assessment"]).first():
                raise serializers.ValidationError({"assessment": "Already started."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the user."""

        validated_data["user"] = self.get_user()
        return super().create(validated_data)


class LPAYakshaScheduleListSerializer(BaseYakshaAssessmentScheduleListSerializer):
    """Serializer for AssignmentYakshaScheduleList."""

    class Meta(BaseYakshaAssessmentScheduleListSerializer.Meta):
        model = LPAYakshaSchedule
        fields = BaseYakshaAssessmentScheduleListSerializer.Meta.fields + ["tracker"]


class LPAYakshaResultListSerializer(BaseYakshaAssessmentResultListSerializer):
    """Serializer class for assignment yaksha result."""

    schedule = LPAYakshaScheduleListSerializer(read_only=True)

    class Meta(BaseYakshaAssessmentResultListSerializer.Meta):
        model = LPAYakshaResult
        fields = BaseYakshaAssessmentResultListSerializer.Meta.fields + ["schedule"]


class UserLPAssessmentListSerializer(LPAssessmentListModelSerializer):
    """Module assignment list serializer"""

    tracker_detail = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the tracker details of assignment."""

        tracker = obj.related_lp_assessment_trackers.filter(user=self.get_user()).first()
        return LPATrackerListSerializer(tracker).data if tracker else None

    def get_is_locked(self, obj):
        """
        Returns if the assessment is locked or not.
        """

        lp_tracker = self.context.get("lp_tracker", None)
        user = self.get_user()
        if not lp_tracker:
            return True
        assessment_tracker = obj.related_lp_assessment_trackers.filter(user=lp_tracker.user).first()
        if (
            (lp_tracker and lp_tracker.is_completed)
            or obj.is_practice
            or not lp_tracker.learning_path.is_dependencies_sequential
            or assessment_tracker
        ):
            return False
        if obj.type == AssessmentTypeChoices.dependent_assessment:
            course_tracker = user.related_user_course_trackers.filter(course=obj.lp_course.course).first()
            previous_assessments = LPAssessment.objects.filter(
                lp_course=obj.lp_course, sequence__lt=obj.sequence, is_practice=False
            )
            previous_assessment_trackers = user.related_lp_assessment_trackers.filter(
                assessment__in=previous_assessments,
            )
            if (
                not course_tracker
                or not course_tracker.is_completed
                or previous_assessments.count() != previous_assessment_trackers.count()
                or previous_assessment_trackers.filter(is_completed=False)
            ):
                return True
            return False
        else:
            previous_lp_courses = obj.learning_path.related_learning_path_courses.all()
            previous_course_trackers = user.related_user_course_trackers.filter(
                course_id__in=previous_lp_courses.values_list("course__id", flat=True)
            )
            previous_final_assessments = LPAssessment.objects.filter(
                learning_path=obj.learning_path,
                sequence__lt=obj.sequence,
                is_practice=False,
            )
            previous_course_assessments = LPAssessment.objects.filter(
                lp_course__learning_path=obj.learning_path,
                lp_course__in=previous_lp_courses,
                is_practice=False,
            )
            previous_assessment_trackers = user.related_lp_assessment_trackers.filter(
                Q(assessment__in=previous_course_assessments) | Q(assessment__in=previous_final_assessments)
            )
            if (
                previous_course_trackers.filter(is_completed=False)
                or previous_assessment_trackers.filter(is_completed=False)
                or previous_lp_courses.count() != previous_course_trackers.count()
                or previous_assessment_trackers.count()
                != previous_final_assessments.count() + previous_course_assessments.count()
            ):
                return True
            return False

    class Meta(LPAssessmentListModelSerializer.Meta):
        fields = LPAssessmentListModelSerializer.Meta.fields + ["tracker_detail", "is_locked"]
