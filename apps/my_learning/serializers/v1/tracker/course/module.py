from django.utils import timezone
from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer
from apps.learning.config import EvaluationTypeChoices
from apps.learning.models import CourseAssessment, CourseAssignment, CourseModule
from apps.learning.serializers.v1 import CourseModuleRetrieveSerializer
from apps.my_learning.models import CourseAssessmentTracker, CourseModuleTracker
from apps.my_learning.serializers.v1 import UserCourseAssessmentListSerializer, UserCourseAssignmentListSerializer


class CourseModuleTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to return the module tracker."""

    class Meta:
        model = CourseModuleTracker
        fields = [
            "id",
            "module",
            "ccms_id",
            "progress",
            "completed_duration",
            "created_by",
            "created_at",
            "is_ccms_obj",
            "is_completed",
            "completion_date",
        ]


class UserCourseModuleListSerializer(CourseModuleRetrieveSerializer):
    """Serializer class for course modules."""

    is_locked = serializers.SerializerMethodField()
    tracker_details = serializers.SerializerMethodField()
    assessments = serializers.SerializerMethodField(read_only=True)
    assignments = serializers.SerializerMethodField(read_only=True)

    def get_module_tracker(self, instance):
        """Returns the module tracker."""

        course_tracker = self.context.get("course_tracker")
        module_tracker = instance.related_course_module_trackers.filter(course_tracker=course_tracker).first()
        self.context["module_tracker"] = module_tracker
        return module_tracker

    def previous_dependencies(self, instance):
        """Returns previous modules & assignment was not completed."""

        user = self.get_user()
        course_tracker = self.context.get("course_tracker")
        previous_modules_objs = (
            CourseModule.objects.alive()
            .filter(
                course=instance.course,
                sequence__lt=instance.sequence,
            )
            .exclude(id=instance.pk)
            .values_list("id", flat=True)
        )
        previous_modules_tracker_qs = CourseModuleTracker.objects.filter(
            course_tracker=course_tracker, module__in=previous_modules_objs
        )
        previous_assessment_objs = CourseAssessment.objects.filter(
            module_id__in=previous_modules_objs, is_practice=False
        ).values_list("id", flat=True)
        previous_assessment_tracker_qs = CourseAssessmentTracker.objects.filter(
            assessment_id__in=previous_assessment_objs, module_tracker__course_tracker__user=self.get_user()
        )
        uncompleted_assessment = previous_assessment_tracker_qs.filter(is_completed=False).first()
        previous_assignment_objs = CourseAssignment.objects.filter(
            module_id__in=previous_modules_objs, assignment__evaluation_type=EvaluationTypeChoices.evaluated
        ).values_list("assignment_id", flat=True)
        previous_assignment_tracker_qs = user.related_assignment_trackers.filter(
            assignment_id__in=previous_assignment_objs
        )
        uncompleted_assignment = previous_assignment_tracker_qs.filter(is_completed=False).first()
        return (
            previous_modules_tracker_qs.count() == previous_modules_objs.count(),
            previous_modules_objs.exists(),
            previous_modules_tracker_qs.filter(is_completed=False).exists(),
            previous_assessment_tracker_qs.count() == previous_assessment_objs.count(),
            True if uncompleted_assessment else False,
            previous_assignment_tracker_qs.count() == previous_assignment_objs.count(),
            True if uncompleted_assignment else False,
        )

    def get_tracker_details(self, obj):
        """Returns the module tracker details."""

        module_tracker = self.get_module_tracker(obj)
        return CourseModuleTrackerListSerializer(module_tracker, context=self.context).data if module_tracker else None

    def get_assessments(self, obj):
        """Returns the list of assessments with tracker details."""

        self.get_module_tracker(obj)
        assessments = obj.related_course_assessments.all().order_by("sequence", "created_at")
        return UserCourseAssessmentListSerializer(assessments, many=True, context=self.context).data

    def get_assignments(self, obj):
        """Returns the list of assignments with tracker details."""

        self.get_module_tracker(obj)
        assignments = obj.related_course_assignments.all().order_by("sequence", "created_at")
        return UserCourseAssignmentListSerializer(assignments, many=True, context=self.context).data

    def get_is_locked(self, obj):
        """
        If the module is sequential then locking system should be enabled. Logic for the same.
        If the module is mandatory and all the previous mandatory models are completed only
        then the current module should be opened otherwise it should be locked
        irrespective of start/end date. If module is not mandatory then it
        can be opened/skipped. As per iiht @Darshan on 09-11-23.

        Used in serializer
        """

        course_tracker = self.context.get("course_tracker")
        module_tracker = self.get_module_tracker(obj)
        if not course_tracker:
            return True
        if course_tracker.is_completed or (module_tracker and module_tracker.is_completed):
            return False
        if obj.start_date and obj.end_date and not obj.start_date <= timezone.now().date() <= obj.end_date:
            return True
        (
            is_module_tracker,
            previous_modules,
            previous_modules_trackers,
            is_assessment_tracker,
            uncompleted_assessment,
            is_assignment_tracker,
            uncompleted_assignment,
        ) = self.previous_dependencies(obj)
        if not previous_modules:
            return False
        elif obj.course.is_dependencies_sequential and (
            not is_module_tracker
            or previous_modules_trackers
            or not is_assessment_tracker
            or uncompleted_assessment
            or not is_assignment_tracker
            or uncompleted_assignment
        ):
            return True
        return False

    class Meta(CourseModuleRetrieveSerializer.Meta):
        fields = CourseModuleRetrieveSerializer.Meta.fields + [
            "tracker_details",
            "is_locked",
        ]


class CourseModuleTrackerCreateSerializer(AppCreateModelSerializer):
    """Serializer class to create a course module tracker."""

    class Meta(AppCreateModelSerializer.Meta):
        model = CourseModuleTracker
        fields = [
            "course_tracker",
            "module",
            "ccms_id",
            "is_ccms_obj",
        ]

    def validate(self, attrs):
        """Validate the course tracker & module is valid or not."""

        course_tracker = attrs.get("course_tracker")
        module = attrs.get("module")
        if course_tracker.user != self.get_user():
            raise serializers.ValidationError({"course_tracker": "Invalid tracker details provided."})
        if attrs["is_ccms_obj"] or course_tracker.is_ccms_obj:
            attrs["module"] = None
            if not attrs["ccms_id"]:
                raise serializers.ValidationError({"ccms_id": "This field is required."})
            if course_tracker.related_course_module_trackers.filter(ccms_id=attrs["ccms_id"]).first():
                raise serializers.ValidationError({"ccms_id": "Already started."})
        else:
            attrs["ccms_id"] = None
            if not module:
                raise serializers.ValidationError({"module": "This field is required."})
            if module not in course_tracker.course.related_course_modules.all():
                raise serializers.ValidationError({"course_tracker": "Invalid module details provided."})
            if course_tracker.related_course_module_trackers.filter(module=module).first():
                raise serializers.ValidationError({"module": "Already started."})
        return attrs
