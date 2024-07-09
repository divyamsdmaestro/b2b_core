from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from apps.common.models.base import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer, AppWriteOnlyModelSerializer
from apps.leaderboard.config import MilestoneChoices
from apps.learning.models import (
    AdvancedLearningPath,
    Assignment,
    AssignmentGroup,
    Course,
    LearningPath,
    Playground,
    PlaygroundGroup,
    SkillTraveller,
)
from apps.learning.serializers.v1 import BaseLearningListModelSerializer, BaseLearningSkillRoleRetrieveModelSerializer
from apps.learning.validators import FileSizeValidator
from apps.my_learning.config import (
    AllBaseLearningTypeChoices,
    BaseLearningTypeChoices,
    EnrollmentTypeChoices,
    LearningStatusChoices,
)
from apps.my_learning.models import Enrollment, FeedbackResponse
from apps.my_learning.tasks import ALPProgressUpdateTask, LPProgressUpdateTask
from apps.tenant_service.middlewares import get_current_db_name

Basic_enrollment_fields = [
    "learning_type",
    "course",
    "learning_path",
    "advanced_learning_path",
    "skill_traveller",
    "playground",
    "playground_group",
    "assignment",
    "assignment_group",
    "ccms_id",
    "is_ccms_obj",
]

BASE_LEARNING_TYPES = [
    BaseLearningTypeChoices.course,
    BaseLearningTypeChoices.learning_path,
    BaseLearningTypeChoices.advanced_learning_path,
]

LEARNING_RELATED_FIELDS = {
    EnrollmentTypeChoices.course: "course",
    EnrollmentTypeChoices.learning_path: "learning_path",
    EnrollmentTypeChoices.advanced_learning_path: "advanced_learning_path",
    EnrollmentTypeChoices.skill_traveller: "skill_traveller",
    EnrollmentTypeChoices.skill_ontology: "skill_ontology",
    EnrollmentTypeChoices.playground: "playground",
    EnrollmentTypeChoices.playground_group: "playground_group",
    EnrollmentTypeChoices.assignment: "assignment",
    EnrollmentTypeChoices.assignment_group: "assignment_group",
}

tracker_related_fields = {
    AllBaseLearningTypeChoices.course: "related_user_course_trackers",
    AllBaseLearningTypeChoices.learning_path: "related_user_learning_path_trackers",
    AllBaseLearningTypeChoices.advanced_learning_path: "related_user_alp_trackers",
    AllBaseLearningTypeChoices.skill_traveller: "related_user_skill_traveller_trackers",
    AllBaseLearningTypeChoices.playground: "related_user_playground_trackers",
    AllBaseLearningTypeChoices.playground_group: "related_user_playground_group_trackers",
    AllBaseLearningTypeChoices.assignment: "related_assignment_trackers",
    AllBaseLearningTypeChoices.assignment_group: "related_assignment_group_trackers",
    EnrollmentTypeChoices.skill_ontology: "related_user_skill_ontology_trackers",
}  # Note: If the related name changed needs to change the value as per related name

RELATED_TRACKERS = {
    "Course": "related_user_course_trackers",
    "LearningPath": "related_user_learning_path_trackers",
    "AdvancedLearningPath": "related_user_alp_trackers",
    "SkillTraveller": "related_user_skill_traveller_trackers",
    "SkillOntology": "related_user_skill_ontology_trackers",
    "Playground": "related_user_playground_trackers",
    "PlaygroundGroup": "related_user_playground_group_trackers",
    "Assignment": "related_assignment_trackers",
    "AssignmentGroup": "related_assignment_group_trackers",
}  # Note: If the model name changed needs to change the key as per model name

RELATED_ENROLLMENT_LEARNING_FIELDS = {
    "Course": "course",
    "LearningPath": "learning_path",
    "AdvancedLearningPath": "advanced_learning_path",
    "SkillTraveller": "skill_traveller",
    "SkillOntology": "skill_ontology",
    "Playground": "playground",
    "PlaygroundGroup": "playground_group",
    "Assignment": "assignment",
    "AssignmentGroup": "assignment_group",
}  # Note: If the model name changed needs to change the key as per model name

RELATED_TRACKER_FIELDS = {
    "UserCourseTracker": "course",
    "UserLearningPathTracker": "learning_path",
    "UserALPTracker": "advanced_learning_path",
    "UserSkillTravellerTracker": "skill_traveller",
    "UserSkillOntologyTracker": "skill_ontology",
    "UserPlaygroundTracker": "playground",
    "UserPlaygroundGroupTracker": "playground_group",
    "AssignmentTracker": "assignment",
    "AssignmentGroupTracker": "assignment_group",
}  # Note: If the model name changed needs to change the key as per model name


class UserBaseLearningListSerializer(BaseLearningListModelSerializer):
    """User base learning list serializer class."""

    enrolled_details = serializers.SerializerMethodField()
    tracker_detail = serializers.SerializerMethodField()
    user_favourite = serializers.SerializerMethodField(read_only=True)

    def user_enrolled_details(self):
        """Returns the user enrolled the course or not."""

        user = self.context.get("request").user
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        return Enrollment.objects.filter(Q(user_group__in=user_groups) | Q(user=user))

    def get_enrolled_details(self, obj):
        """Returns the user enrolled the course or not."""

        enrollment_instance = (
            self.user_enrolled_details()
            .filter(**{RELATED_ENROLLMENT_LEARNING_FIELDS[self.Meta.model.__name__]: obj.id})
            .first()
        )
        return (
            BaseEnrollmentListModelSerializer(enrollment_instance, context=self.context).data
            if enrollment_instance
            else None
        )

    def get_tracker_detail(self, obj):
        """Returns the tracker details."""

        user = self.get_user()
        tracker_instance = getattr(obj, RELATED_TRACKERS[self.Meta.model.__name__]).filter(user=user).first()

        return (
            {
                "id": tracker_instance.id,
                "progress": tracker_instance.progress,
                "completed_duration": tracker_instance.completed_duration,
                "last_accessed_on": tracker_instance.last_accessed_on,
                "completion_date": tracker_instance.completion_date,
                "is_completed": tracker_instance.is_completed,
            }
            if tracker_instance
            else None
        )

    def get_user_favourite(self, obj):
        """Returns True if the Course is marked as a favorite by user, otherwise False."""

        user_favourite = obj.related_user_favourites.filter(user=self.get_user()).first()
        return {"id": user_favourite.id if user_favourite else None, "is_favourite": bool(user_favourite)}

    class Meta(BaseLearningListModelSerializer.Meta):
        fields = BaseLearningListModelSerializer.Meta.fields + [
            "description",
            "rating",
            "enrolled_details",
            "tracker_detail",
            "user_favourite",
        ]


class UserBaseLearningCertificateListSerializer(UserBaseLearningListSerializer):
    """User base learning certificate list serializer class."""

    class Meta(UserBaseLearningListSerializer.Meta):
        fields = UserBaseLearningListSerializer.Meta.fields + [
            "certificate",
            "is_trending",
            "is_popular",
            "is_recommended",
        ]


class UserBaseLearningRetrieveModelSerializer(
    BaseLearningSkillRoleRetrieveModelSerializer, UserBaseLearningListSerializer
):
    """User base learning retrieve model serializer with skill & role."""

    is_feedback_given = serializers.SerializerMethodField(read_only=True)

    def get_is_feedback_given(self, obj):
        """Returns the user is submitted feedback or not"""

        return bool(
            FeedbackResponse.objects.filter(
                learning_type=RELATED_ENROLLMENT_LEARNING_FIELDS[self.Meta.model.__name__],
                learning_type_id=obj.id,
                question__feedback_template__in=obj.feedback_template.all(),
                user=self.get_user(),
            )
        )

    class Meta(BaseLearningSkillRoleRetrieveModelSerializer.Meta):
        fields = BaseLearningSkillRoleRetrieveModelSerializer.Meta.fields + [
            "enrolled_details",
            "tracker_detail",
            "user_favourite",
            "is_feedback_given",
        ]


class BaseLearningFKCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for base foreign key fields."""

    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.alive(),
        required=False,
    )
    learning_path = serializers.PrimaryKeyRelatedField(
        queryset=LearningPath.objects.alive(),
        required=False,
    )
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.alive(),
        required=False,
    )
    skill_traveller = serializers.PrimaryKeyRelatedField(
        queryset=SkillTraveller.objects.alive(),
        required=False,
    )
    playground = serializers.PrimaryKeyRelatedField(
        queryset=Playground.objects.alive(),
        required=False,
    )
    playground_group = serializers.PrimaryKeyRelatedField(
        queryset=PlaygroundGroup.objects.alive(),
        required=False,
    )
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.alive(), required=False)
    assignment_group = serializers.PrimaryKeyRelatedField(queryset=AssignmentGroup.objects.alive(), required=False)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        fields = [
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
            "playground",
            "playground_group",
            "assignment",
            "assignment_group",
        ]


class BaseYakshaAssessmentScheduleListSerializer(AppReadOnlyModelSerializer):
    """Base serializer for YakshaScheduleList."""

    class Meta:
        fields = [
            "id",
            "scheduled_id",
            "wecp_invite_id",
            "scheduled_link",
            "created_at",
        ]


class BaseYakshaAssessmentResultListSerializer(AppReadOnlyModelSerializer):
    """Base serializer class for yaksha assessment result."""

    class Meta:
        fields = [
            "id",
            "attempt",
            "duration",
            "total_questions",
            "answered",
            "progress",
            "start_time",
            "end_time",
            "is_pass",
        ]


class BaseEnrollmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for user's enrolled list."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Enrollment
        fields = Basic_enrollment_fields + [
            "id",
            "uuid",
            "user",
            "user_group",
            "created_by",
            "action",
            "reason",
            "approval_type",
            "actionee",
            "is_enrolled",
            "learning_status",
            "created_at",
            "start_date",
            "end_date",
            "action_date",
            "skill_ontology",
        ]


class BaseAssessmentTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for assessment tracker list."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = [
            "id",
            "uuid",
            "ccms_id",
            "allowed_attempt",
            "available_attempt",
            "progress",
            "completion_date",
            "start_date",
            "is_completed",
            "is_pass",
            "is_ccms_obj",
            "created_at",
        ]


class BaseMultipleFileUploadSerializer(AppSerializer):
    """Serializer for handle multiple files."""

    file = serializers.ListField(
        child=serializers.FileField(
            max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
            allow_empty_file=False,
            use_url=False,
            validators=[FileSizeValidator(120)],
        )
    )


class BaseEnrollmentTrackerCreateSerializer(AppWriteOnlyModelSerializer):
    """Common serializer class to creating trackers for enrollments."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        fields = [
            "enrollment",
            "ccms_id",
            "is_ccms_obj",
        ]

    def validate(self, attrs):
        """Validating the learning instance enrolled and already started."""

        enrollment = attrs["enrollment"]
        user = self.get_user()
        if enrollment.user != user and enrollment.user_group not in user.related_user_groups.all():
            raise serializers.ValidationError({"enrollment": "Detail not found."})
        if not enrollment.is_enrolled:
            raise serializers.ValidationError({"enrollment": "Approval is pending."})
        tracker_instances = self.Meta.model.objects.filter(user=user)
        if attrs["is_ccms_obj"]:
            if not (ccms_id := attrs["ccms_id"]):
                raise serializers.ValidationError({"ccms_id": "This field is required."})
            if tracker_instances.filter(ccms_id=ccms_id).exists():
                raise serializers.ValidationError({"enrollment": "Already started."})
        else:
            tracker_field = RELATED_TRACKER_FIELDS.get(self.Meta.model.__name__)
            tracker_instance = attrs.get(tracker_field)
            if not tracker_instance:
                raise serializers.ValidationError({tracker_field: "This field is required."})
            if tracker_instances.filter(**{tracker_field: tracker_instance}).exists():
                raise serializers.ValidationError({"enrollment": "Already started."})
            self.context.update({"tracker_field": tracker_field})
        return attrs

    def create(self, validated_data):
        """Create a tracker for course."""

        from apps.my_learning.models import UserALPTracker, UserLearningPathTracker

        user = validated_data["user"] = self.get_user()
        is_ccms_obj = validated_data["is_ccms_obj"]
        tracker_model = getattr(user, self.Meta.model._meta.default_related_name)
        if not is_ccms_obj:
            tracker_field = self.context["tracker_field"]
            tracker_instance = validated_data.pop(tracker_field)
            instance, created = tracker_model.get_or_create(
                **{tracker_field: tracker_instance}, defaults=validated_data
            )
        else:
            ccms_id = validated_data.pop("ccms_id", None)
            instance, created = tracker_model.get_or_create(ccms_id=ccms_id, defaults=validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        request = {"headers": dict(self.context["request"].headers)}
        if isinstance(instance, UserLearningPathTracker):
            instance.call_leaderboard_task(
                milestone_names=MilestoneChoices.learning_path_starter, request_headers=request
            )
            transaction.on_commit(
                lambda: LPProgressUpdateTask().run_task(
                    db_name=get_current_db_name(), lp_tracker_id=instance.id, request=request
                )
            )
        elif isinstance(instance, UserALPTracker):
            instance.call_leaderboard_task(
                milestone_names=MilestoneChoices.certification_path_starter, request_headers=request
            )
            transaction.on_commit(
                lambda: ALPProgressUpdateTask().run_task(
                    db_name=get_current_db_name(), alp_tracker_id=instance.id, request=request
                )
            )
        return instance
