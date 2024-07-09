from rest_framework import serializers

from apps.access.models import User
from apps.access_control.config import RoleTypeChoices
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer
from apps.learning.config import (
    AssignmentGuidanceChoices,
    AssignmentTypeChoices,
    EvaluationTypeChoices,
    PlaygroundToolChoices,
)
from apps.learning.models import (
    Assignment,
    AssignmentDocument,
    AssignmentResource,
    AssignmentSubTopic,
    AssignmentTopic,
)
from apps.learning.serializers.v1 import (
    BaseAssignmentCUDModelSerializer,
    BaseAssignmentRetrieveModelSerializer,
    BaseLearningListModelSerializer,
    CommonResourceCreateModelSerializer,
    CommonResourceListModelSerializer,
)

ASSIGNMENT_COMMON_FIELDS = [
    "file",
    "author",
    "topic",
    "subtopic",
    "skill",
    "role",
    "mml_sku_id",
    "assessment_uuid",
    "vm_name",
    "type",
    "tool",
    "guidance_type",
    "guidance_text",
    "reference",
    "version",
    "duration",
    "evaluation_type",
    "allowed_attempts",
    "reminder_date",
    "send_reminder",
    "enable_submission",
]


class AssignmentDocumentRetrieveModelSerializer(AppReadOnlyModelSerializer):
    """Assignment image retrieve model serializer."""

    class Meta:
        model = AssignmentDocument
        fields = ["id", "file"]


class AssignmentCUDModelSerializer(BaseAssignmentCUDModelSerializer):
    """Assignment CUD model serializer."""

    topic = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, allow_null=True)
    subtopic = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, allow_null=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(roles__role_type=RoleTypeChoices.author), many=True
    )

    class Meta(BaseAssignmentCUDModelSerializer.Meta):
        model = Assignment
        fields = BaseAssignmentCUDModelSerializer.Meta.fields + ASSIGNMENT_COMMON_FIELDS

    def validate(self, attrs):
        """Overridden to validate the assignment tool."""

        super().validate(attrs)
        tool = attrs["tool"]
        if tool == PlaygroundToolChoices.yaksha and attrs["assessment_uuid"] is None:
            raise serializers.ValidationError({"assessment_uuid": "This field is required."})
        if tool == PlaygroundToolChoices.mml:
            if attrs["mml_sku_id"] is None:
                raise serializers.ValidationError({"mml_sku_id": "This field is required."})
            if attrs["vm_name"] is None:
                raise serializers.ValidationError({"vm_name": "This field is required."})
        if attrs["send_reminder"] and attrs["reminder_date"] is None:
            raise serializers.ValidationError({"reminder_date": "This field is required."})
        if attrs["guidance_type"] == AssignmentGuidanceChoices.guided:
            if not attrs.get("guidance_text") and not attrs.get("file"):
                raise serializers.ValidationError(
                    {"guidance_text": "This field is required.", "file": "This field is required."}
                )
        return attrs

    def topic_subtopic_creation(self, topic, subtopic):
        """Create if the object does not exist."""

        topic = AssignmentTopic.objects.get_or_create(name=topic)[0] if topic else None
        subtopic = (
            AssignmentSubTopic.objects.get_or_create(name=subtopic, topic=topic)[0] if topic and subtopic else None
        )
        return topic, subtopic

    def create(self, validated_data):
        """Overridden to create some necessary fields on the flow."""

        validated_data["topic"], validated_data["subtopic"] = self.topic_subtopic_creation(
            topic=validated_data["topic"], subtopic=validated_data["subtopic"]
        )
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """Overridden to create some necessary fields on the flow."""

        validated_data["topic"], validated_data["subtopic"] = self.topic_subtopic_creation(
            topic=validated_data["topic"], subtopic=validated_data["subtopic"]
        )
        instance = super().update(instance, validated_data)
        return instance

    def get_meta(self) -> dict:
        """Returns the metadata."""

        meta = super().get_meta()
        meta.update(
            {
                "type": self.serialize_dj_choices(AssignmentTypeChoices.choices),
                "tool": self.serialize_dj_choices(PlaygroundToolChoices.choices[:2]),  # Restricted codelabs choice.
                "evaluation_type": self.serialize_dj_choices(EvaluationTypeChoices.choices),
                "guidance_type": self.serialize_dj_choices(AssignmentGuidanceChoices.choices),
            }
        )
        return meta

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["topic"] = self.instance.topic.name if self.instance.topic else None
        meta["subtopic"] = self.instance.subtopic.name if self.instance.subtopic else None
        return meta


class AssignmentListModelSerializer(BaseLearningListModelSerializer):
    """Assignment list serializer."""

    file = AssignmentDocumentRetrieveModelSerializer(read_only=True)
    highlight = serializers.ListField(source="highlight_as_list", read_only=True)
    skill = serializers.SerializerMethodField(read_only=True)

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    class Meta(BaseLearningListModelSerializer.Meta):
        model = Assignment
        fields = BaseLearningListModelSerializer.Meta.fields + [
            "highlight",
            "skill",
            "type",
            "file",
            "tool",
            "enable_submission",
            "guidance_type",
            "guidance_text",
        ]

    def get_filter_meta(self):
        """Returns the filter meta."""

        meta = super().get_filter_meta()
        meta.update(
            {
                "type": self.serialize_dj_choices(AssignmentTypeChoices.choices),
                "tool": self.serialize_dj_choices(PlaygroundToolChoices.choices[:2]),  # Restricted codelabs choice.
            }
        )
        return meta


class AssignmentRetrieveModelSerializer(BaseAssignmentRetrieveModelSerializer):
    """Assignment retrieve model serializer."""

    file = AssignmentDocumentRetrieveModelSerializer(read_only=True)

    class Meta(BaseAssignmentRetrieveModelSerializer.Meta):
        model = Assignment
        fields = BaseAssignmentRetrieveModelSerializer.Meta.fields + ASSIGNMENT_COMMON_FIELDS


class AssignmentResourceCreateModelSerializer(CommonResourceCreateModelSerializer):
    """Serializer class to upload assignment resources."""

    class Meta(CommonResourceCreateModelSerializer.Meta):
        model = AssignmentResource
        fields = CommonResourceCreateModelSerializer.Meta.fields + ["assignment"]


class AssignmentResourceListModelSerializer(CommonResourceListModelSerializer):
    """Serializer class to list the assignment resources."""

    class Meta(CommonResourceListModelSerializer.Meta):
        model = AssignmentResource
