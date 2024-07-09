from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import EvaluationTypeChoices
from apps.learning.models import SkillTraveller, STAssessment, STAssignment
from apps.learning.serializers.v1 import SkillTravellerCourseModelListSerializer, SkillTravellerRetrieveModelSerializer
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import UserSkillTravellerTracker
from apps.my_learning.serializers.v1 import (
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
    UserCourseListSerializer,
    UserCourseTrackerListSerializer,
    UserSTAssessmentListSerializer,
    UserSTAssignmentListSerializer,
)


class UserSkillTravellerListSerializer(UserBaseLearningCertificateListSerializer):
    """Serializer class to list the skill_traveller list with enrollment details."""

    skill = serializers.SerializerMethodField(read_only=True)
    highlight = serializers.ListField(source="highlight_as_list")

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    class Meta(UserBaseLearningCertificateListSerializer.Meta):
        model = SkillTraveller
        fields = UserBaseLearningCertificateListSerializer.Meta.fields + [
            "journey_type",
            "learning_type",
            "skill",
            "highlight",
        ]


class UserSkillTravellerRetrieveSerializer(
    SkillTravellerRetrieveModelSerializer, UserBaseLearningRetrieveModelSerializer
):
    """Serializer class to retrieve the skill_traveller details."""

    class Meta(SkillTravellerRetrieveModelSerializer.Meta):
        fields = SkillTravellerRetrieveModelSerializer.Meta.fields + [
            "enrolled_details",
            "tracker_detail",
            "user_favourite",
            "is_feedback_given",
        ]


class UserSkillTravellerTrackerCreateSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to add the skill tracker traveller.."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserSkillTravellerTracker
        fields = [
            "enrollment",
            "skill_traveller",
        ]

    def validate(self, attrs):
        """Overridden to check the enrolled course list."""

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
            .related_user_skill_traveller_trackers.filter(skill_traveller=attrs["skill_traveller"])
            .first()
        ):
            raise serializers.ValidationError({"enrollment": "Already started."})
        return attrs

    def create(self, validated_data):
        """Create a tracker for course."""

        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        instance.skill_traveller_progress_update()
        return instance


class UserSkillTravellerCourseListSerializer(SkillTravellerCourseModelListSerializer):
    """Serializer class to list the skill_traveller_courses list with tracker details."""

    tracker_detail = serializers.SerializerMethodField()
    course = UserCourseListSerializer(read_only=True)
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
            self.context["is_tracker_exists"] = False
            data = None
        return data

    def get_is_start_hidden(self, obj):
        """Returns True if the content is locked."""

        st = obj.skill_traveller
        if not st.is_dependencies_sequential or self.context["is_tracker_exists"]:
            return False
        if obj.sequence == 1:
            return obj.is_lock_active
        user = self.get_user()
        previous_st_courses = st.related_skill_traveller_courses.filter(sequence__lt=obj.sequence)
        previous_course_trackers = user.related_user_course_trackers.filter(
            course_id__in=previous_st_courses.values_list("course_id", flat=True)
        )
        previous_assessments = STAssessment.objects.filter(
            st_course__skill_traveller=st, st_course__in=previous_st_courses, is_practice=False
        )
        previous_assessment_trackers = user.related_st_assessment_trackers.filter(assessment__in=previous_assessments)
        previous_assignments = STAssignment.objects.filter(
            st_course__skill_traveller=st,
            st_course__in=previous_st_courses,
            assignment__evaluation_type=EvaluationTypeChoices.evaluated,
        ).values_list("assignment_id", flat=True)
        previous_assignment_trackers = user.related_assignment_trackers.filter(assignment_id__in=previous_assignments)
        if (
            obj.is_lock_active
            or previous_st_courses.count() != previous_course_trackers.count()
            or previous_assessments.count() != previous_assessment_trackers.count()
            or previous_assignments.count() != previous_assignment_trackers.count()
            or previous_course_trackers.filter(is_completed=False)
            or previous_assessment_trackers.filter(is_completed=False)
            or previous_assignment_trackers.filter(is_completed=False)
        ):
            return True
        return False

    def get_assessments(self, obj):
        """Returns a list of st_course assessments."""

        assessments = obj.related_st_assessments.all().order_by("sequence")
        self.context["st_tracker"] = obj.skill_traveller.related_user_skill_traveller_trackers.filter(
            user=self.get_user()
        ).first()
        return UserSTAssessmentListSerializer(assessments, many=True, context=self.context).data

    def get_assignments(self, obj):
        """Returns a list of st_course assignments."""

        assignments = obj.related_st_assignments.all().order_by("sequence")
        self.context["st_tracker"] = obj.skill_traveller.related_user_skill_traveller_trackers.filter(
            user=self.get_user()
        ).first()
        return UserSTAssignmentListSerializer(assignments, many=True, context=self.context).data

    class Meta(SkillTravellerCourseModelListSerializer.Meta):
        fields = SkillTravellerCourseModelListSerializer.Meta.fields + [
            "tracker_detail",
            "is_start_hidden",
            "assessments",
            "assignments",
        ]


class UserSkillTravellerTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list st trackers."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserSkillTravellerTracker
        fields = [
            "id",
            "skill_traveller",
            "enrollment",
            "progress",
            "completed_duration",
            "last_accessed_on",
            "is_completed",
            "completion_date",
        ]
