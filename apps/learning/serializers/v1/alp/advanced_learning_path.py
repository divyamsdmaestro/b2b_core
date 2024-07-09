from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import LearningTypeChoices
from apps.learning.models import AdvancedLearningPath, AdvancedLearningPathResource, ALPLearningPath
from apps.learning.serializers.v1 import (
    BaseLearningListModelSerializer,
    BaseLearningSkillRoleCUDModelSerializer,
    BaseLearningSkillRoleRetrieveModelSerializer,
    CommonResourceCreateModelSerializer,
    CommonResourceListModelSerializer,
    LearningPathListModelSerializer,
)
from apps.learning.validators import learning_type_field_validation


class AdvancedLearningPathCUDModelSerializer(BaseLearningSkillRoleCUDModelSerializer):
    """Advanced Learning path CUD serializer"""

    class Meta(BaseLearningSkillRoleCUDModelSerializer.Meta):
        model = AdvancedLearningPath
        fields = BaseLearningSkillRoleCUDModelSerializer.Meta.fields + [
            "learning_type",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validations"""

        super().validate(attrs)
        learning_type_field_validation(attrs)
        return attrs

    def create(self, validated_data):
        """Overridden to change the active field when the data to be save as draft."""

        validated_data["is_active"] = False
        instance = super().create(validated_data=validated_data)
        instance.role.all().role_advanced_learning_path_count_update()
        instance.skill.all().skill_advanced_learning_path_count_update()
        instance.category.category_advanced_learning_path_count_update()
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the skill, role& category learning_path count & the draft field to instance."""

        instance = super().update(instance=instance, validated_data=validated_data)
        instance.role.all().role_advanced_learning_path_count_update()
        instance.skill.all().skill_advanced_learning_path_count_update()
        instance.category.category_advanced_learning_path_count_update()
        return instance

    def get_meta(self) -> dict:
        """Get meta & initial values for learning_paths."""

        metadata = super().get_meta()
        metadata["learning_type"] = self.serialize_dj_choices(LearningTypeChoices.choices)
        return metadata


class AdvancedLearningPathListModelSerializer(BaseLearningListModelSerializer):
    """Advanced learning path list model serializer."""

    class Meta(BaseLearningListModelSerializer.Meta):
        model = AdvancedLearningPath
        fields = BaseLearningListModelSerializer.Meta.fields + [
            "no_of_lp",
        ]

    def get_filter_meta(self):
        """Return the filter meta."""

        data = super().get_filter_meta()
        data["learning_type"] = self.serialize_dj_choices(LearningTypeChoices.choices)
        return data


class AdvancedLearningPathRetrieveModelSerializer(BaseLearningSkillRoleRetrieveModelSerializer):
    """Advanced learning path retrieve model serializer."""

    class Meta(BaseLearningSkillRoleRetrieveModelSerializer.Meta):
        model = AdvancedLearningPath
        fields = BaseLearningSkillRoleRetrieveModelSerializer.Meta.fields + [
            "learning_type",
            "no_of_lp",
        ]


class ALPLearningPathListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to retrieve list of alp's learning_path list."""

    learning_path = LearningPathListModelSerializer(read_only=True)

    class Meta:
        model = ALPLearningPath
        fields = [
            "id",
            "advanced_learning_path",
            "learning_path",
            "sequence",
            "is_mandatory",
        ]


class ALPLearningPathCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for assign the courses to learning paths."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = ALPLearningPath
        fields = [
            "advanced_learning_path",
            "learning_path",
            "is_mandatory",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validation."""

        learning_path, alp = attrs["learning_path"], attrs["advanced_learning_path"]
        learning_paths = alp.related_alp_learning_paths.all()
        if self.instance:
            learning_paths = learning_paths.exclude(id=self.instance.id)
        if learning_paths.filter(learning_path=learning_path).first():
            raise serializers.ValidationError({"learning_path": "Learning path is already present."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the duration & count."""

        alp = validated_data["advanced_learning_path"]
        max_position = alp.related_alp_learning_paths.order_by("-sequence").values_list("sequence", flat=True).first()
        validated_data["sequence"] = max_position + 1 if max_position else 1

        instance = super().create(validated_data)
        instance.advanced_learning_path.duration_lp_count_update()
        return instance


class AlpResourceCreateModelSerializer(CommonResourceCreateModelSerializer):
    """Serializer class to upload advanced learning path resources."""

    class Meta(CommonResourceCreateModelSerializer.Meta):
        model = AdvancedLearningPathResource
        fields = CommonResourceCreateModelSerializer.Meta.fields + ["advanced_learning_path"]


class AlpResourceListModelSerializer(CommonResourceListModelSerializer):
    """Serializer class to list the advanced learning path resources."""

    class Meta(CommonResourceListModelSerializer.Meta):
        model = AdvancedLearningPathResource
