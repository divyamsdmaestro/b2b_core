from rest_framework import serializers

from apps.access.models import User
from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer
from apps.common.helpers import process_request_headers
from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSerializer,
    AppWriteOnlyModelSerializer,
    BaseIDNameSerializer,
)
from apps.learning.config import ExpertLearningTypeChoices
from apps.learning.models import AdvancedLearningPath, Course, Expert, LearningPath
from apps.my_learning.config import ActionChoices
from apps.tenant_service.middlewares import get_current_tenant_details


class ExpertCUDModelSerializer(AppWriteOnlyModelSerializer):
    """`Expert` model serializer holds create, update & destroy."""

    # TODO: Chat microservices update is not handled as it involves chats and deletion is chat service.

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive(), required=False)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.alive(), required=False)
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.alive(), required=False
    )

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Expert
        fields = [
            "user",
            "learning_type",
            "course",
            "learning_path",
            "advanced_learning_path",
        ]

    def validate(self, attrs):
        """Validate if the selected learning_type corresponding field is not empty."""

        learning_type = attrs.get("learning_type")
        if not attrs.get(learning_type, None):
            raise serializers.ValidationError({f"{learning_type}": "This field is required."})
        if attrs[learning_type].related_experts.filter(user=attrs["user"], learning_type=learning_type):
            raise serializers.ValidationError(
                {f"{learning_type}": f"The selected user is already an expert in this {learning_type}."}
            )
        if not attrs[learning_type].is_assign_expert:
            raise serializers.ValidationError(
                {f"{learning_type}": f"Cannot assign an expert to this {learning_type} as it is restricted."}
            )
        return attrs

    def create(self, validated_data):
        """Overridden to make user as expert in chat microservices."""

        instance = super().create(validated_data)
        if instance.action == ActionChoices.approved:
            learning_type = validated_data["learning_type"]
            if learning_type == ExpertLearningTypeChoices.course:
                course = validated_data.get("course")
                request = self.get_request()
                request_headers = process_request_headers(request={"headers": dict(request.headers)})
                tenant_details = get_current_tenant_details()
                if tenant_details["is_keycloak"]:
                    user_id = instance.user.uuid
                else:
                    user_id = instance.user.idp_id
                chat_user_data = {
                    "first_name": instance.user.first_name,
                    "last_name": instance.user.last_name,
                    "email": instance.user.email,
                    "user_id": user_id,
                }
                course.register_user_to_course_in_chat(
                    user_id=None, request_headers=request_headers, user_data=chat_user_data, is_expert=True
                )
        return instance

    def get_meta(self) -> dict:
        """Get meta & initial values."""

        return {
            "user": self.serialize_for_meta(User.objects.active(), fields=["id", "username"]),
            "course": self.serialize_for_meta(Course.objects.alive(), fields=["id", "name"]),
            "learning_path": self.serialize_for_meta(LearningPath.objects.alive(), fields=["id", "name"]),
            "advanced_learning_path": self.serialize_for_meta(
                AdvancedLearningPath.objects.alive(), fields=["id", "name"]
            ),
            "learning_type": self.serialize_dj_choices(ExpertLearningTypeChoices.choices),
        }


class ExpertListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `Expert` model."""

    course = BaseIDNameSerializer(read_only=True)
    learning_path = BaseIDNameSerializer(read_only=True)
    advanced_learning_path = BaseIDNameSerializer(read_only=True)
    user = SimpleUserReadOnlyModelSerializer()
    skills = serializers.SerializerMethodField()

    def get_skills(self, obj):
        """Returns a list of skills of an expert"""

        learning_obj = getattr(obj, obj.learning_type, None)
        return learning_obj.skill.values_list("name", flat=True) if learning_obj else None

    class Meta:
        model = Expert
        fields = [
            "id",
            "uuid",
            "user",
            "course",
            "learning_path",
            "advanced_learning_path",
            "learning_type",
            "action",
            "skills",
            "is_created_by_admin",
        ]


class ExpertApprovalSerializer(AppSerializer):
    """Serializer class for Expert Approval."""

    expert = serializers.PrimaryKeyRelatedField(queryset=Expert.objects.filter(action=ActionChoices.pending))
    action = serializers.ChoiceField(choices=ActionChoices.choices)
