from django.db.models import Q
from rest_framework import serializers

from apps.learning.config import AssessmentTypeChoices
from apps.learning.models import STAssessment
from apps.learning.serializers.v1 import STAssessmentListModelSerializer
from apps.my_learning.models import STAssessmentTracker, STAYakshaResult, STAYakshaSchedule
from apps.my_learning.serializers.v1 import (
    BaseAssessmentTrackerListSerializer,
    BaseYakshaAssessmentResultListSerializer,
    BaseYakshaAssessmentScheduleListSerializer,
)


class STATrackerListSerializer(BaseAssessmentTrackerListSerializer):
    """Skill Traveller assessment tracker list serializer."""

    class Meta(BaseAssessmentTrackerListSerializer.Meta):
        model = STAssessmentTracker
        fields = [
            "assessment",
            "user",
        ] + BaseAssessmentTrackerListSerializer.Meta.fields


class STAYakshaScheduleListSerializer(BaseYakshaAssessmentScheduleListSerializer):
    """Serializer for AssessmentYakshaScheduleList."""

    class Meta(BaseYakshaAssessmentScheduleListSerializer.Meta):
        model = STAYakshaSchedule
        fields = BaseYakshaAssessmentScheduleListSerializer.Meta.fields + ["tracker"]


class STAYakshaResultListSerializer(BaseYakshaAssessmentResultListSerializer):
    """Serializer class for assessment yaksha result."""

    schedule = STAYakshaScheduleListSerializer(read_only=True)

    class Meta(BaseYakshaAssessmentResultListSerializer.Meta):
        model = STAYakshaResult
        fields = BaseYakshaAssessmentResultListSerializer.Meta.fields + ["schedule"]


class UserSTAssessmentListSerializer(STAssessmentListModelSerializer):
    """SkillTraveller assessment list serializer"""

    tracker_detail = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the tracker details of assessment."""

        tracker = obj.related_st_assessment_trackers.filter(user=self.get_user()).first()
        return STATrackerListSerializer(tracker).data if tracker else None

    def get_is_locked(self, obj):
        """
        Returns if the assessment is locked or not.
        """

        st_tracker = self.context.get("st_tracker", None)
        user = self.get_user()
        if not st_tracker:
            return True
        assessment_tracker = obj.related_st_assessment_trackers.filter(user=st_tracker.user).first()
        if (
            (st_tracker and st_tracker.is_completed)
            or obj.is_practice
            or not st_tracker.skill_traveller.is_dependencies_sequential
            or assessment_tracker
        ):
            return False
        if obj.type == AssessmentTypeChoices.dependent_assessment:
            course_tracker = user.related_user_course_trackers.filter(course=obj.st_course.course).first()
            previous_assessments = STAssessment.objects.filter(
                st_course=obj.st_course, sequence__lt=obj.sequence, is_practice=False
            )
            previous_assessment_trackers = user.related_st_assessment_trackers.filter(
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
            previous_st_courses = obj.skill_traveller.related_skill_traveller_courses.all()
            previous_course_trackers = user.related_user_course_trackers.filter(
                course_id__in=previous_st_courses.values_list("course__id", flat=True)
            )
            previous_final_assessments = STAssessment.objects.filter(
                skill_traveller=obj.skill_traveller,
                sequence__lt=obj.sequence,
                is_practice=False,
            )
            previous_course_assessments = STAssessment.objects.filter(
                st_course__skill_traveller=obj.skill_traveller,
                st_course__in=previous_st_courses,
                is_practice=False,
            )
            previous_assessment_trackers = user.related_st_assessment_trackers.filter(
                Q(assessment__in=previous_course_assessments) | Q(assessment__in=previous_final_assessments)
            )
            if (
                previous_course_trackers.filter(is_completed=False)
                or previous_assessment_trackers.filter(is_completed=False)
                or previous_st_courses.count() != previous_course_trackers.count()
                or previous_assessment_trackers.count()
                != previous_final_assessments.count() + previous_course_assessments.count()
            ):
                return True
            return False

    class Meta(STAssessmentListModelSerializer.Meta):
        fields = STAssessmentListModelSerializer.Meta.fields + ["tracker_detail", "is_locked"]
