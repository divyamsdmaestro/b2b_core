from rest_framework import serializers

from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSpecificImageFieldSerializer,
    AppWriteOnlyModelSerializer,
    BaseIDNameSerializer,
)
from apps.learning.config import LearningUpdateTypeChoices
from apps.learning.models import AdvancedLearningPath, Course, LearningPath, LearningUpdate, SkillTraveller
from apps.my_learning.config import BaseLearningTypeChoices


class LearningUpdateCUDModelSerializer(AppWriteOnlyModelSerializer):
    """`LearningUpdate` model serializer holds create, update & destroy."""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive(), required=False)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.alive(), required=False)
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.alive(), required=False
    )
    skill_traveller = serializers.PrimaryKeyRelatedField(queryset=SkillTraveller.objects.alive(), required=False)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = LearningUpdate
        fields = [
            "name",
            "description",
            "learning_update_image",
            "learning_type",
            "update_type",
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
        ]

    def validate(self, attrs):
        """Validate if the selected learning_type corresponding field is not empty."""

        learning_type = attrs.get("learning_type")
        if not attrs.get(learning_type, None):
            raise serializers.ValidationError({f"{learning_type}": "This field is required."})
        return attrs

    def get_meta(self) -> dict:
        """Get meta & initial values."""

        return {
            "learning_type": self.serialize_dj_choices(BaseLearningTypeChoices.choices),
            "update_type": [
                {  # TODO: Need to give support for other LearningUpdateTypeChoices.
                    "id": LearningUpdateTypeChoices.announcement,
                    "name": LearningUpdateTypeChoices.labels.announcement,
                }
            ],
        }


class LearningUpdateListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `LearningUpdate` model."""

    learning_update_image = AppSpecificImageFieldSerializer(read_only=True)
    course = BaseIDNameSerializer()
    learning_path = BaseIDNameSerializer()
    advanced_learning_path = BaseIDNameSerializer()
    skill_traveller = BaseIDNameSerializer()

    class Meta:
        model = LearningUpdate
        fields = [
            "id",
            "name",
            "learning_update_image",
            "created_at",
            "update_type",
            "description",
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
        ]
