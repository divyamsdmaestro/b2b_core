from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer
from apps.learning.config import EvaluationTypeChoices, LearningTypeChoices
from apps.learning.models import LearningPath, LPAssessment, LPAssignment
from apps.learning.serializers.v1 import LPCourseListModelSerializer
from apps.my_learning.models import UserLearningPathTracker
from apps.my_learning.serializers.v1 import (
    BaseEnrollmentTrackerCreateSerializer,
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
    UserCourseListSerializer,
    UserCourseTrackerListSerializer,
    UserLPAssessmentListSerializer,
    UserLPAssignmentListSerializer,
)


class UserLearningPathListSerializer(UserBaseLearningCertificateListSerializer):
    """Serializer class to list the learning_path list with enrollment details."""

    skill = serializers.SerializerMethodField(read_only=True)
    highlight = serializers.ListField(source="highlight_as_list")

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    class Meta(UserBaseLearningCertificateListSerializer.Meta):
        model = LearningPath
        fields = UserBaseLearningCertificateListSerializer.Meta.fields + [
            "no_of_courses",
            "skill",
            "highlight",
        ]

    def get_filter_meta(self):
        """Return the filter meta."""

        data = super().get_filter_meta()
        data["learning_type"] = self.serialize_dj_choices(LearningTypeChoices.choices)
        return data


class UserLearningPathRetrieveSerializer(UserBaseLearningRetrieveModelSerializer):
    """Serializer class to retrieve the learning_path details."""

    class Meta(UserBaseLearningRetrieveModelSerializer.Meta):
        model = LearningPath
        fields = UserBaseLearningRetrieveModelSerializer.Meta.fields + [
            "learning_type",
            "no_of_courses",
        ]


class UserLearningPathTrackerCreateModelSerializer(BaseEnrollmentTrackerCreateSerializer):
    """Serializer class to enroll the learning_path."""

    class Meta(BaseEnrollmentTrackerCreateSerializer.Meta):
        model = UserLearningPathTracker
        fields = BaseEnrollmentTrackerCreateSerializer.Meta.fields + [
            "learning_path",
        ]


class UserLearningPathCourseListSerializer(LPCourseListModelSerializer):
    """Serializer class to list the learning_path_courses list with tracker details."""

    tracker_detail = serializers.SerializerMethodField()
    course = UserCourseListSerializer()
    is_start_hidden = serializers.SerializerMethodField()
    assessments = serializers.SerializerMethodField(read_only=True)
    assignments = serializers.SerializerMethodField(read_only=True)

    def get_tracker_detail(self, obj):
        """Returns the course tracker data."""

        user = self.context.get("request").user
        tracker_instance = obj.course.related_user_course_trackers.filter(user=user).first()
        if tracker_instance:
            data = UserCourseTrackerListSerializer(tracker_instance).data
            self.context["is_tracker_exists"] = True
        else:
            data = None
            self.context["is_tracker_exists"] = False
        return data

    def get_is_start_hidden(self, obj):
        """Returns True if the content is locked."""

        lp = obj.learning_path
        if not lp.is_dependencies_sequential or self.context["is_tracker_exists"]:
            return False
        if obj.sequence == 1:
            return obj.is_lock_active
        user = self.get_user()
        previous_lp_courses = lp.related_learning_path_courses.filter(
            course__is_deleted=False, sequence__lt=obj.sequence
        )
        previous_course_trackers = user.related_user_course_trackers.filter(
            course_id__in=previous_lp_courses.values_list("course_id", flat=True)
        )
        previous_assessments = LPAssessment.objects.filter(
            lp_course__learning_path=lp, lp_course__in=previous_lp_courses, is_practice=False
        )
        previous_assessment_trackers = user.related_lp_assessment_trackers.filter(assessment__in=previous_assessments)
        previous_assignments = LPAssignment.objects.filter(
            lp_course__learning_path=lp,
            lp_course__in=previous_lp_courses,
            assignment__evaluation_type=EvaluationTypeChoices.evaluated,
        ).values_list("assignment_id", flat=True)
        previous_assignment_trackers = user.related_assignment_trackers.filter(assignment_id__in=previous_assignments)
        if (
            obj.is_lock_active
            or previous_lp_courses.count() != previous_course_trackers.count()
            or previous_assessments.count() != previous_assessment_trackers.count()
            or previous_assignments.count() != previous_assignment_trackers.count()
            or previous_course_trackers.filter(is_completed=False)
            or previous_assessment_trackers.filter(is_completed=False)
            or previous_assignment_trackers.filter(is_completed=False)
        ):
            return True
        return False

    def get_assessments(self, obj):
        """Returns a list of lp_course assessments."""

        assessments = obj.related_lp_assessments.all().order_by("sequence")
        self.context["lp_tracker"] = obj.learning_path.related_user_learning_path_trackers.filter(
            user=self.get_user()
        ).first()
        return UserLPAssessmentListSerializer(assessments, many=True, context=self.context).data

    def get_assignments(self, obj):
        """Returns a list of lp_course assignments."""

        assignments = obj.related_lp_assignments.all().order_by("sequence")
        self.context["lp_tracker"] = obj.learning_path.related_user_learning_path_trackers.filter(
            user=self.get_user()
        ).first()
        return UserLPAssignmentListSerializer(assignments, many=True, context=self.context).data

    class Meta(LPCourseListModelSerializer.Meta):
        fields = LPCourseListModelSerializer.Meta.fields + [
            "tracker_detail",
            "is_start_hidden",
            "assessments",
            "assignments",
        ]


class UserLearningPathTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list lp trackers."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserLearningPathTracker
        fields = [
            "id",
            "learning_path",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "completion_date",
        ]
