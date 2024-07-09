from rest_framework import serializers

from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSerializer,
    AppSpecificImageFieldSerializer,
    AppUpdateModelSerializer,
    AppWriteOnlyModelSerializer,
)
from apps.learning.config import ProficiencyChoices
from apps.learning.models import Category, CategoryRole, CategorySkill, RoleSkillRelation
from apps.learning.serializers.v1 import CommonTalentManagementCUDModelSerializer, CommonTalentManagementListSerializer


class CategoryRoleCUDModelSerializer(CommonTalentManagementCUDModelSerializer):
    """Role model serializer holds create, update & destroy."""

    class _Serializer(AppSerializer):
        """Serializer class for role relate skills."""

        skill = serializers.PrimaryKeyRelatedField(queryset=CategorySkill.objects.active())
        required_proficiency = serializers.ChoiceField(choices=ProficiencyChoices.choices)

    skill_detail = _Serializer(write_only=True, many=True, required=True, allow_null=True)

    class Meta(CommonTalentManagementCUDModelSerializer.Meta):
        model = CategoryRole
        fields = CommonTalentManagementCUDModelSerializer.Meta.fields + [
            "category",
            "skill_detail",
        ]

    def update(self, instance, validated_data):
        """Overridden to update the draft filed as false."""

        validated_data["is_draft"] = False
        instance = super().update(instance=instance, validated_data=validated_data)
        return instance

    def get_meta(self) -> dict:
        """Get meta & the  initial values for CourseRole."""

        return {"category": self.serialize_for_meta(Category.objects.alive(), fields=["id", "name"])}


class CategoryRoleListSerializer(CommonTalentManagementListSerializer):
    """Role model list serializer."""

    class Meta(CommonTalentManagementListSerializer.Meta):
        model = CategoryRole
        fields = CommonTalentManagementListSerializer.Meta.fields


class CategoryRoleRetrieveSerializer(AppReadOnlyModelSerializer):
    """Role model retrieve serializer."""

    image = AppSpecificImageFieldSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = CategoryRole
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
            "no_of_st",
            "no_of_tp",
            "no_of_tpg",
            "created_at",
        ]


class CategoryRoleStatusUpdateSerializer(AppUpdateModelSerializer):
    """Update model serializer to  update the status of role."""

    class Meta(AppUpdateModelSerializer.Meta):
        model = CategoryRole
        fields = ["is_active", "is_archive"]


class RoleSkillCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for RoleSkillCUD."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = RoleSkillRelation
        fields = [
            "role",
            "skill",
            "required_proficiency",
        ]
