from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from apps.access.models import User
from apps.access_control.models import UserGroup
from apps.access_control.serializers.v1 import UserGroupReadOnlySerializer
from apps.common.helpers import process_request_headers
from apps.common.serializers import (
    AppCreateModelSerializer,
    AppReadOnlyModelSerializer,
    AppSerializer,
    AppUpdateModelSerializer,
    AppWriteOnlyModelSerializer,
    BaseIDNameImageSerializer,
    BaseIDNameSerializer,
)
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
from apps.learning.serializers.v1 import SkillOntologyListModelSerializer
from apps.my_learning.config import (
    ActionChoices,
    AllBaseLearningTypeChoices,
    ApprovalTypeChoices,
    BaseLearningTypeChoices,
    LearningStatusChoices,
)
from apps.my_learning.helpers import get_ccms_tracker_details, get_tracker_instance
from apps.my_learning.models import Enrollment, EnrollmentReminder
from apps.my_learning.serializers.v1 import (
    BASE_LEARNING_TYPES,
    LEARNING_RELATED_FIELDS,
    BaseEnrollmentListModelSerializer,
    Basic_enrollment_fields,
    tracker_related_fields,
)
from apps.my_learning.tasks import CalendarActivityCreationTask, UserEnrollmentEmailTask
from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_details
from apps.virtutor.tasks import SessionParticipantUpdateTask


class UserEnrollmentCreateModelSerializer(AppCreateModelSerializer):
    """Serializer for create Enrollment."""

    ccms_obj_name = serializers.CharField(required=False, allow_null=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = Enrollment
        fields = Basic_enrollment_fields + ["ccms_obj_name"]

    def validate(self, attrs):
        """Validate the fields based on enrollment type."""

        learning_type = attrs.get("learning_type")
        learning_type_field = LEARNING_RELATED_FIELDS.get(learning_type)
        required_field_instance = attrs.get(learning_type_field)
        if attrs.get("is_ccms_obj"):
            required_field_instance = attrs.get("ccms_id")
        user = self.get_user()
        if not required_field_instance:
            raise serializers.ValidationError({learning_type_field: "This field is required."})
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        if Enrollment.objects.filter(
            Q(user_group__in=user_groups) | Q(user=user),
            **{learning_type_field: required_field_instance},
        ).first():
            raise serializers.ValidationError({learning_type_field: f"{learning_type} is already enrolled."})
        return attrs

    def create(self, validated_data):
        """Create a new enrollment."""

        ccms_obj_name = validated_data.pop("ccms_obj_name", "CCMS")
        learning_type = validated_data.pop("learning_type")
        learning_instance = validated_data.pop(learning_type) if not validated_data["is_ccms_obj"] else None
        user = self.get_user()
        idp_token = self.get_request().headers.get("idp-token")
        request_headers = process_request_headers({"headers": dict(self.context["request"].headers)})
        validated_data["start_date"] = learning_instance.start_date if learning_instance else None
        validated_data["user"] = user
        validated_data["action_date"] = timezone.now().date()
        tenant_details = get_current_tenant_details()
        validated_data["is_enrolled"] = False
        validated_data["created_by"] = user
        if not validated_data["is_ccms_obj"]:
            instance, created = user.related_enrollments.get_or_create(
                **{"learning_type": learning_type, learning_type: learning_instance}, defaults=validated_data
            )
        else:
            instance, created = user.related_enrollments.get_or_create(
                learning_type=learning_type, ccms_id=validated_data["ccms_id"], defaults=validated_data
            )
        unlocked_catalogue = (
            learning_instance.related_learning_catalogues.filter(
                Q(related_catalogue_relations__user_group__id__in=user.related_user_groups.values_list("id"))
                | Q(related_catalogue_relations__user=user),
                is_locked=False,
                is_self_enroll_enabled=True,
            ).exists()
            if learning_instance
            else True
        )
        if tenant_details["is_self_enroll_enabled"] and unlocked_catalogue:
            instance.approval_type = ApprovalTypeChoices.self_enrolled
            instance.is_enrolled = True
            instance.reason = "Self enroll enabled."
            instance.action = ActionChoices.approved
            tracker_instance = get_tracker_instance(user=user, enrollment_instance=instance)
            if tracker_instance:
                instance.learning_status = LearningStatusChoices.started
            instance.save()
            instance.notify_user(ccms_obj_name=ccms_obj_name)
            instance.call_leaderboard_tasks(request_headers=request_headers)
        if not instance.is_ccms_obj:
            if instance.is_enrolled and learning_type == BaseLearningTypeChoices.course:
                if tenant_details["is_keycloak"]:
                    user_id = instance.user.uuid
                else:
                    user_id = instance.user.idp_id
                instance.course.register_user_to_course_in_chat(user_id=[user_id], request_headers=request_headers)
            if instance.is_enrolled and learning_type in BASE_LEARNING_TYPES:
                # TODO: Handle for SSO.
                SessionParticipantUpdateTask().run_task(
                    learning_type=learning_type,
                    learning_instance_id=learning_instance.id,
                    user_id=user.id,
                    idp_token=idp_token,
                    db_name=get_current_db_name(),
                )
                CalendarActivityCreationTask().run_task(
                    event_type=learning_type,
                    event_instance_id=learning_instance.id,
                    user_ids=user.id,
                    db_name=get_current_db_name(),
                )
            UserEnrollmentEmailTask().run_task(
                user_id=user.id, enrollment_id=instance.id, db_name=get_current_db_name()
            )
        return instance


class EnrollmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for list model serializer."""

    course = BaseIDNameSerializer(read_only=True)
    learning_path = BaseIDNameSerializer(read_only=True)
    advanced_learning_path = BaseIDNameSerializer(read_only=True)
    skill_traveller = BaseIDNameSerializer(read_only=True)
    playground = BaseIDNameSerializer(read_only=True)
    playground_group = BaseIDNameSerializer(read_only=True)
    assignment = BaseIDNameSerializer(read_only=True)
    assignment_group = BaseIDNameSerializer(read_only=True)
    skill_ontology = BaseIDNameSerializer(read_only=True)
    user = BaseIDNameSerializer(read_only=True)
    user_group = UserGroupReadOnlySerializer(read_only=True)
    created_by = BaseIDNameSerializer(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Enrollment
        fields = Basic_enrollment_fields + [
            "id",
            "uuid",
            "user",
            "roles",
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

    def get_roles(self, obj):
        """Returns the User's role"""

        return BaseIDNameSerializer(obj.user.roles, many=True).data if obj.user else None

    def to_representation(self, instance):
        """Overridden to return the ccms detail if it was a ccms obj."""

        from apps.learning.helpers import get_ccms_retrieve_details

        results = super().to_representation(instance)
        if instance.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type=instance.learning_type,
                instance_id=str(instance.ccms_id),
                request={"headers": dict(self.context["request"].headers)},
            )
            if success:
                results["ccms_id"] = data["data"]
        return results


class BaseAuthorSerializer(BaseIDNameImageSerializer):
    """Common Serializer to retrieve the id, name, image and auther information."""

    author = BaseIDNameSerializer(read_only=True)


class UserEnrollmentListModelSerializer(BaseEnrollmentListModelSerializer):
    """Serializer class for user's enrolled list."""

    class _LPSerializer(BaseIDNameImageSerializer):
        """Serializer class for LP list in enrollment list serializer."""

        no_of_courses = serializers.IntegerField()

    class _STSerializer(BaseIDNameImageSerializer):
        """Serializer class for skill traveller detail with learning type."""

        learning_type = serializers.CharField()

    class _AssignmentSerializer(BaseIDNameImageSerializer):
        """Serializer class for assignment group detail with type."""

        type = serializers.CharField()
        author = BaseIDNameSerializer(many=True)

    course = BaseAuthorSerializer(read_only=True)
    learning_path = _LPSerializer(read_only=True)
    advanced_learning_path = BaseIDNameImageSerializer(read_only=True)
    skill_traveller = _STSerializer(read_only=True)
    skill_ontology = SkillOntologyListModelSerializer(read_only=True)
    playground = BaseIDNameImageSerializer(read_only=True)
    playground_group = BaseIDNameImageSerializer(read_only=True)
    assignment = _AssignmentSerializer(read_only=True)
    assignment_group = BaseIDNameImageSerializer(read_only=True)
    tracker_detail = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the tracker details."""

        user = self.get_user()
        if obj.is_enrolled and obj.learning_type in tracker_related_fields and not obj.is_ccms_obj:
            tracker_instance = (
                getattr(user, tracker_related_fields[obj.learning_type])
                .filter(
                    **{
                        obj.learning_type: getattr(obj, obj.learning_type).id
                        if getattr(obj, obj.learning_type)
                        else None
                    }
                )
                .first()
            )
            return (
                {
                    "id": tracker_instance.id,
                    "progress": tracker_instance.progress,
                    "completed_duration": tracker_instance.completed_duration,
                    "last_accessed_on": tracker_instance.last_accessed_on,
                    "is_completed": tracker_instance.is_completed,
                    "completion_date": tracker_instance.completion_date,
                }
                if tracker_instance
                else None
            )
        elif obj.is_enrolled and obj.is_ccms_obj:
            return get_ccms_tracker_details(user=user, learning_type=obj.learning_type, ccms_id=obj.ccms_id)
        return None

    class Meta(BaseEnrollmentListModelSerializer.Meta):
        fields = BaseEnrollmentListModelSerializer.Meta.fields + ["tracker_detail"]

    def to_representation(self, instance):
        """Overridden to return the ccms detail if it was a ccms obj."""

        from apps.learning.helpers import get_ccms_retrieve_details

        results = super().to_representation(instance)
        if instance.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type=instance.learning_type,
                instance_id=str(instance.ccms_id),
                request={"headers": dict(self.context["request"].headers)},
            )
            if success:
                results["ccms_id"] = data["data"]
        return results


class UserEnrollmentUpdateModelSerializer(AppUpdateModelSerializer):
    """Serializer class for update the user enrollments."""

    ccms_obj_name = serializers.CharField(required=False, allow_null=True)

    class Meta(AppUpdateModelSerializer.Meta):
        model = Enrollment
        fields = ["action", "approval_type", "reason", "end_date", "ccms_obj_name"]

    def update(self, instance, validated_data):
        """Overridden to update the is_enrolled fields."""

        ccms_obj_name = validated_data.pop("ccms_obj_name", "CCMS")
        action = validated_data["action"]
        idp_token = self.get_request().headers.get("idp-token")
        request_headers = process_request_headers({"headers": dict(self.context["request"].headers)})
        validated_data["is_enrolled"] = False
        if action == ActionChoices.approved:
            validated_data["is_enrolled"] = True
        instance: Enrollment = super().update(instance, validated_data)
        instance.call_leaderboard_tasks(request_headers=dict(self.context["request"].headers))
        if instance.is_enrolled:
            instance.notify_user(ccms_obj_name=ccms_obj_name)
            if instance.learning_type == BaseLearningTypeChoices.course and instance.user and not instance.is_ccms_obj:
                tenant_details = get_current_tenant_details()
                if tenant_details["is_keycloak"]:
                    user_id = instance.user.uuid
                else:
                    user_id = instance.user.idp_id
                instance.course.register_user_to_course_in_chat(user_id=[user_id], request_headers=request_headers)
            tracker_instance = get_tracker_instance(user=self.get_user(), enrollment_instance=instance)
            if tracker_instance:
                instance.learning_status = LearningStatusChoices.started
            if self.instance.learning_type in BASE_LEARNING_TYPES and not instance.is_ccms_obj:
                SessionParticipantUpdateTask().run_task(
                    learning_type=self.instance.learning_type,
                    learning_instance_id=getattr(self.instance, self.instance.learning_type).id,
                    user_id=self.instance.user.id,
                    idp_token=idp_token,
                    db_name=get_current_db_name(),
                )
                CalendarActivityCreationTask().run_task(
                    event_type=self.instance.learning_type,
                    event_instance_id=getattr(self.instance, self.instance.learning_type).id,
                    user_ids=self.instance.user.id,
                    db_name=get_current_db_name(),
                )
        return instance

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {
            "action": ActionChoices.choices,
            "approval_type": ApprovalTypeChoices.choices,
        }


class UserBulkEnrollSerializer(AppSerializer):
    """Serializer class to bulk enroll the users."""

    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.active(), many=True)
    user_group = serializers.PrimaryKeyRelatedField(queryset=UserGroup.objects.alive(), many=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.unarchived(), many=True)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.unarchived(), many=True)
    alp = serializers.PrimaryKeyRelatedField(queryset=AdvancedLearningPath.objects.unarchived(), many=True)
    skill_traveller = serializers.PrimaryKeyRelatedField(queryset=SkillTraveller.objects.unarchived(), many=True)
    playground = serializers.PrimaryKeyRelatedField(queryset=Playground.objects.unarchived(), many=True)
    playground_group = serializers.PrimaryKeyRelatedField(queryset=PlaygroundGroup.objects.unarchived(), many=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.unarchived(), many=True)
    assignment_group = serializers.PrimaryKeyRelatedField(queryset=AssignmentGroup.objects.unarchived(), many=True)
    end_date = serializers.DateTimeField(required=True)


class EnrollmentReminderCUDModelSerializer(AppWriteOnlyModelSerializer):
    """CUD Serializer for `EnrollmentReminder` model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = EnrollmentReminder
        fields = [
            "learning_type",
            "days",
        ]

    def get_meta(self) -> dict:
        """get meta data."""

        return {
            "learning_type": self.serialize_dj_choices(AllBaseLearningTypeChoices.choices)[:3],
        }


class EnrollmentReminderListModelSerializer(AppReadOnlyModelSerializer):
    """List Serializer for `EnrollmentReminder` model."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = EnrollmentReminder
        fields = [
            "id",
            "learning_type",
            "days",
        ]
