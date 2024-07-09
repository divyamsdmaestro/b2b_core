from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, BaseIDNameSerializer
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.learning.config import CommonLearningAssignmentTypeChoices, EvaluationTypeChoices
from apps.learning.models import Course, CourseAssignment, LearningPath, SkillOntology
from apps.learning.serializers.v1 import CourseAssignmentListModelSerializer
from apps.meta.serializers.v1 import FacultyListModelSerializer
from apps.my_learning.config import EnrollmentTypeChoices, LearningStatusChoices
from apps.my_learning.models import AssignmentTracker, Enrollment, UserCourseTracker
from apps.my_learning.serializers.v1 import (
    BaseEnrollmentTrackerCreateSerializer,
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
)


class UserCourseListSerializer(UserBaseLearningCertificateListSerializer):
    """Serializer class to retrieve all the enrolled courses with enrollment details."""

    skill = BaseIDNameSerializer(many=True, read_only=True)
    author = BaseIDNameSerializer(read_only=True)
    highlight = serializers.ListField(source="highlight_as_list", read_only=True)

    class Meta(UserBaseLearningCertificateListSerializer.Meta):
        model = Course
        fields = UserBaseLearningCertificateListSerializer.Meta.fields + [
            "highlight",
            "skill",
            "author",
        ]


class UserCourseRetrieveModelSerializer(UserBaseLearningRetrieveModelSerializer):
    """Serializer class to retrieve the detailed course details with its enrollment details."""

    forums = serializers.ListField(source="forum_as_id", read_only=True)
    author = FacultyListModelSerializer(read_only=True)

    class Meta(UserBaseLearningRetrieveModelSerializer.Meta):
        model = Course
        fields = UserBaseLearningRetrieveModelSerializer.Meta.fields + [
            "author",
            "vm_name",
            "mml_sku_id",
            "total_modules",
            "total_sub_modules",
        ]


class UserCourseTrackerCreateModelSerializer(BaseEnrollmentTrackerCreateSerializer):
    """
    Serializer class to start the course & add the trackers for both modules & sub_modules.

    NOTE: Any changes in sequence or locking should also be reflected in
    `UserSkillTravellerCourseListSerializer` & `UserLearningPathCourseListSerializer
    """

    learning_path = serializers.PrimaryKeyRelatedField(
        queryset=LearningPath.objects.unarchived(), allow_null=True, required=False
    )
    skill_ontology = serializers.PrimaryKeyRelatedField(
        queryset=SkillOntology.objects.all(), allow_null=True, required=False
    )

    class Meta(BaseEnrollmentTrackerCreateSerializer.Meta):
        model = UserCourseTracker
        fields = BaseEnrollmentTrackerCreateSerializer.Meta.fields + [
            "course",
            "learning_path",
            "skill_ontology",
        ]

    def validate(self, attrs):
        """Overridden to check the enrolled course list."""

        super().validate(attrs)
        user = self.get_user()
        enrollment: Enrollment = attrs["enrollment"]
        course = attrs["course"]
        learning_path = attrs.get("learning_path", None)

        if not attrs["is_ccms_obj"]:
            match enrollment.learning_type:
                case EnrollmentTypeChoices.course:
                    self.course_validation(enrollment, course, user)
                case EnrollmentTypeChoices.learning_path:
                    self.lp_validation(enrollment.learning_path, course, user)
                case EnrollmentTypeChoices.advanced_learning_path:
                    self.alp_validation(enrollment.advanced_learning_path, learning_path, course, user)
                case EnrollmentTypeChoices.skill_traveller:
                    self.st_validation(enrollment.skill_traveller, course, user)
                case EnrollmentTypeChoices.skill_ontology:
                    if user != enrollment.skill_ontology.user:
                        raise serializers.ValidationError({"skill_ontology": "Invalid Skill Ontology"})
                case _:
                    raise serializers.ValidationError({"enrollment": "Invalid enrollment learning type."})
        return attrs

    @staticmethod
    def course_lock_validation(previous_courses, related_course, user, is_dependencies_sequential):
        """Course Locking logic based on Learning Path Or Skill Traveller."""

        if not is_dependencies_sequential:
            return True
        if related_course.is_lock_active:
            raise serializers.ValidationError({"course": "The selected Course is locked."})
        if related_course.sequence == 1:
            return True
        previous_trackers = user.related_user_course_trackers.filter(course_id__in=previous_courses)
        if not previous_trackers or previous_trackers.filter(is_completed=False).exists():
            raise serializers.ValidationError({"course": "The selected Course is locked."})

    @staticmethod
    def course_validation(enrollment, course, user):
        """Validation logic based on Course enrollment."""

        if enrollment.course != course:
            raise serializers.ValidationError({"course": "Invalid Course"})

    def lp_validation(self, learning_path: LearningPath, course, user):
        """Validation logic based on Learning Path enrollment."""

        related_lp_course = learning_path.related_learning_path_courses.filter(course=course).first()
        if not related_lp_course:
            raise serializers.ValidationError({"course": "Invalid Course"})

        previous_related_lp_courses = learning_path.related_learning_path_courses.filter(
            sequence__lt=related_lp_course.sequence
        ).values_list("course_id", flat=True)
        return self.course_lock_validation(
            previous_related_lp_courses, related_lp_course, user, learning_path.is_dependencies_sequential
        )

    def alp_validation(self, alp, lp, course, user):
        """Validation logic based on Advance Learning Path enrollment."""

        if not lp or not alp.related_alp_learning_paths.filter(learning_path=lp).exists():
            raise serializers.ValidationError({"learning_path": "Invalid learning path."})
        return self.lp_validation(lp, course, user)

    def st_validation(self, skill_traveller, course, user):
        """Validation logic based on Skill Traveller enrollment."""

        related_st_course = skill_traveller.related_skill_traveller_courses.filter(course=course).first()
        if not related_st_course:
            raise serializers.ValidationError({"course": "Invalid Course"})
        previous_related_st_courses = skill_traveller.related_skill_traveller_courses.filter(
            sequence__lt=related_st_course.sequence
        ).values_list("course_id", flat=True)
        return self.course_lock_validation(
            previous_related_st_courses, related_st_course, user, skill_traveller.is_dependencies_sequential
        )

    def create(self, validated_data):
        """Create a tracker for course."""

        validated_data.pop("learning_path", None)
        validated_data.pop("skill_ontology", None)
        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        return instance


class UserCourseTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list course trackers."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserCourseTracker
        fields = [
            "id",
            "course",
            "ccms_id",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "is_ccms_obj",
            "completion_date",
        ]


class UserCourseAssignmentListSerializer(CourseAssignmentListModelSerializer):
    """Module assignment list serializer"""

    tracker_detail = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the tracker details of assignment."""

        tracker = obj.assignment.related_assignment_trackers.filter(user=self.get_user()).first()
        return (
            read_serializer(
                meta_model=AssignmentTracker,
                meta_fields=[
                    "id",
                    "assignment",
                    "enrollment",
                    "progress",
                    "completed_duration",
                    "allowed_attempt",
                    "available_attempt",
                    "last_accessed_on",
                    "is_pass",
                    "is_completed",
                    "completion_date",
                ],
            )(tracker).data
            if tracker
            else None
        )

    def get_is_locked(self, obj):
        """Returns if the assignment is locked or not."""

        user = self.get_user()
        tracker = obj.assignment.related_assignment_trackers.filter(user=user).first()
        course_tracker = self.context.get("course_tracker", None)
        module_tracker = self.context.get("module_tracker", None)
        if (
            (course_tracker and course_tracker.is_completed)
            or (tracker and tracker.is_completed)
            or obj.assignment.evaluation_type == EvaluationTypeChoices.non_evaluated
        ):
            return False
        if obj.type == CommonLearningAssignmentTypeChoices.final_assignment:
            previous_instance = getattr(obj, "course")
            is_dependencies_sequential = previous_instance.is_dependencies_sequential
        else:
            previous_instance = getattr(obj, "module")
            is_dependencies_sequential = previous_instance.course.is_dependencies_sequential
        previous_assignments = previous_instance.related_course_assignments.filter(
            sequence__lt=obj.sequence
        ).values_list("assignment_id", flat=True)
        user_assignment_trackers_qs = user.related_assignment_trackers.filter(assignment_id__in=previous_assignments)
        if obj.type == CommonLearningAssignmentTypeChoices.final_assignment and is_dependencies_sequential:
            related_module_trackers = course_tracker.related_course_module_trackers.all()
            module_assignments = CourseAssignment.objects.filter(
                module_id__in=related_module_trackers.values_list("module_id", flat=True),
                assignment__evaluation_type=EvaluationTypeChoices.evaluated,
            ).values_list("assignment_id", flat=True)
            completed_assignment_trackers = user.related_assignment_trackers.filter(
                assignment_id__in=module_assignments
            ).values_list("is_completed", flat=True)
            completed_module_trackers = related_module_trackers.values_list("is_completed", flat=True)
            if (
                False in completed_module_trackers
                or False in completed_assignment_trackers
                or (user_assignment_trackers_qs and user_assignment_trackers_qs.filter(is_completed=False).exists())
            ):
                return True
            else:
                return False
        if (
            is_dependencies_sequential
            and (module_tracker and not module_tracker.is_completed)
            or not module_tracker
            or not previous_assignments.count() == user_assignment_trackers_qs.count()
            or (user_assignment_trackers_qs and user_assignment_trackers_qs.filter(is_completed=False).exists())
        ):
            return True
        return False

    class Meta(CourseAssignmentListModelSerializer.Meta):
        fields = CourseAssignmentListModelSerializer.Meta.fields + ["tracker_detail", "is_locked"]
