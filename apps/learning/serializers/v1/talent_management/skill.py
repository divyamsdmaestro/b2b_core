from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSpecificImageFieldSerializer,
    AppUpdateModelSerializer,
)
from apps.learning.models import Category, CategorySkill
from apps.learning.serializers.v1 import CommonTalentManagementCUDModelSerializer, CommonTalentManagementListSerializer
from apps.learning.validators import draft_action


class CategorySkillCUDModelSerializer(CommonTalentManagementCUDModelSerializer):
    """Skill model serializer holds create, update & destroy."""

    class Meta(CommonTalentManagementCUDModelSerializer.Meta):
        model = CategorySkill
        fields = CommonTalentManagementCUDModelSerializer.Meta.fields + [
            "category",
        ]

    def create(self, validated_data):
        """Overridden to change the active field when the data to be save as draft."""

        validated_data = draft_action(validated_data)
        instance = super().create(validated_data=validated_data)
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the draft filed as false."""

        validated_data["is_draft"] = False
        instance = super().update(instance=instance, validated_data=validated_data)
        return instance

    def get_meta(self) -> dict:
        """Get meta & the  initial values for CourseRole."""

        return {"category": self.serialize_for_meta(Category.objects.alive(), fields=["id", "name"])}


class CategorySkillListSerializer(CommonTalentManagementListSerializer):
    """Skill model list serializer."""

    class Meta(CommonTalentManagementListSerializer.Meta):
        model = CategorySkill
        fields = CommonTalentManagementListSerializer.Meta.fields


class CategorySkillRetrieveSerializer(AppReadOnlyModelSerializer):
    """Skill model retrieve serializer."""

    image = AppSpecificImageFieldSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = CategorySkill
        fields = [
            "id",
            "name",
            "description",
            "image",
            "is_draft",
            "is_archive",
            "is_active",
            "is_popular",
            "is_recommended",
            "category",
            "no_of_course",
            "no_of_lp",
            "no_of_alp",
            "no_of_tp",
            "no_of_tpg",
            "no_of_st",
            "created_at",
        ]


class CategorySkillStatusUpdateSerializer(AppUpdateModelSerializer):
    """Update model serializer to  update the status of skill."""

    class Meta(AppUpdateModelSerializer.Meta):
        model = CategorySkill
        fields = ["is_active", "is_archive"]
