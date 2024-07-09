from django.db.models import Q
from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer
from apps.learning.config import AssessmentTypeChoices
from apps.learning.serializers.v1 import CourseAssessmentListModelSerializer
from apps.my_learning.models import CAYakshaResult, CAYakshaSchedule, CourseAssessmentTracker
from apps.my_learning.serializers.v1 import (
    BaseAssessmentTrackerListSerializer,
    BaseYakshaAssessmentResultListSerializer,
    BaseYakshaAssessmentScheduleListSerializer,
)


class CATrackerListSerializer(BaseAssessmentTrackerListSerializer):
    """Course assessment tracker list serializer."""

    class Meta(BaseAssessmentTrackerListSerializer.Meta):
        model = CourseAssessmentTracker
        fields = [
            "assessment",
            "module_tracker",
            "course_tracker",
        ] + BaseAssessmentTrackerListSerializer.Meta.fields


class CAYakshaScheduleListSerializer(BaseYakshaAssessmentScheduleListSerializer):
    """Serializer for AssignmentYakshaScheduleList."""

    class Meta(BaseYakshaAssessmentScheduleListSerializer.Meta):
        model = CAYakshaSchedule
        fields = BaseYakshaAssessmentScheduleListSerializer.Meta.fields + ["tracker"]


class CAYakshaResultListSerializer(BaseYakshaAssessmentResultListSerializer):
    """Serializer class for assignment yaksha result."""

    schedule = CAYakshaScheduleListSerializer(read_only=True)

    class Meta(BaseYakshaAssessmentResultListSerializer.Meta):
        model = CAYakshaResult
        fields = BaseYakshaAssessmentResultListSerializer.Meta.fields + ["schedule"]


class UserCourseAssessmentListSerializer(CourseAssessmentListModelSerializer):
    """Module assignment list serializer"""

    tracker_detail = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the tracker details of assignment."""

        user = self.get_user()
        if obj.type == AssessmentTypeChoices.dependent_assessment:
            tracker = obj.related_course_assessment_trackers.filter(module_tracker__course_tracker__user=user).first()
        else:
            tracker = obj.related_course_assessment_trackers.filter(course_tracker__user=user).first()
        return CATrackerListSerializer(tracker).data if tracker else None

    def get_is_locked(self, obj):
        """Returns if the assignment is locked or not."""

        course_tracker = self.context.get("course_tracker", None)
        module_tracker = self.context.get("module_tracker", None)
        if not course_tracker and not module_tracker:
            return True
        if course_tracker.is_completed or obj.is_practice or not course_tracker.course.is_dependencies_sequential:
            return False
        if obj.type == AssessmentTypeChoices.dependent_assessment:
            if obj.related_course_assessment_trackers.filter(module_tracker=module_tracker).first():
                return False
            uncompleted_previous_assessment = CourseAssessmentTracker.objects.filter(
                module_tracker=module_tracker,
                assessment__sequence__lt=obj.sequence,
                assessment__is_practice=False,
                is_completed=False,
            )
            if not module_tracker or not module_tracker.is_completed or uncompleted_previous_assessment.exists():
                return True
            return False
        else:
            if obj.related_course_assessment_trackers.filter(course_tracker=course_tracker).first():
                return False
            uncompleted_previous_assessment = CourseAssessmentTracker.objects.filter(
                Q(module_tracker__in=course_tracker.related_course_module_trackers.all())
                | Q(course_tracker=course_tracker, assessment__sequence__lt=obj.sequence),
                assessment__is_practice=False,
                is_completed=False,
            )
            uncompleted_previous_module = course_tracker.related_course_module_trackers.filter(is_completed=False)
            if uncompleted_previous_module.exists() or uncompleted_previous_assessment.exists():
                return True
            return False

    class Meta(CourseAssessmentListModelSerializer.Meta):
        fields = CourseAssessmentListModelSerializer.Meta.fields + ["tracker_detail", "is_locked"]


class CATrackerCreateSerializer(AppCreateModelSerializer):
    """Serializer class to create a course assessments."""

    class Meta(AppCreateModelSerializer.Meta):
        model = CourseAssessmentTracker
        fields = [
            "assessment",
            "course_tracker",
            "module_tracker",
            "ccms_id",
            "is_ccms_obj",
        ]

    def validate(self, attrs):
        """Validate the assessment is valid or not."""

        course_tracker = attrs.get("course_tracker")
        module_tracker = attrs.get("module_tracker")
        if not course_tracker and not module_tracker:
            raise serializers.ValidationError({"tracker": "Either course or module tracker is required."})
        if course_tracker:
            user = course_tracker.user
            is_ccms_obj = course_tracker.is_ccms_obj
            assessments = course_tracker.course.related_course_assessments.all() if not is_ccms_obj else []
            trackers = course_tracker.related_course_assessment_trackers.all()
        else:
            user = module_tracker.course_tracker.user
            is_ccms_obj = module_tracker.is_ccms_obj
            assessments = module_tracker.module.related_course_assessments.all() if not is_ccms_obj else []
            trackers = module_tracker.related_course_assessment_trackers.all()
        if user != self.get_user():
            raise serializers.ValidationError({"tracker": "Invalid tracker details provided."})
        if attrs["is_ccms_obj"] or is_ccms_obj:
            attrs["assessment"] = None
            if not attrs["ccms_id"]:
                raise serializers.ValidationError({"ccms_id": "This field is required."})
            if trackers.filter(ccms_id=attrs["ccms_id"]).first():
                raise serializers.ValidationError({"ccms_id": "Already started."})
        else:
            attrs["ccms_id"] = None
            if not attrs["assessment"]:
                raise serializers.ValidationError({"assessment": "This field is required."})
            if attrs["assessment"] not in assessments:
                raise serializers.ValidationError({"assessment": "Detail not found."})
            if trackers.filter(assessment=attrs["assessment"]).first():
                raise serializers.ValidationError({"assessment": "Already started."})
        return attrs
