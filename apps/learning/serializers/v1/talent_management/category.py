from apps.common.serializers import AppUpdateModelSerializer
from apps.learning.models import Category
from apps.learning.serializers.v1 import CommonTalentManagementCUDModelSerializer, CommonTalentManagementListSerializer
from apps.learning.validators import draft_action


class CategoryCUDModelSerializer(CommonTalentManagementCUDModelSerializer):
    """Category model serializer holds create, update & destroy."""

    class Meta(CommonTalentManagementCUDModelSerializer.Meta):
        model = Category
        fields = CommonTalentManagementCUDModelSerializer.Meta.fields

    def create(self, validated_data):
        """Overridden to change the active field when the data to be save as draft."""

        validated_data = draft_action(validated_data)
        instance = super().create(validated_data=validated_data)
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the is_draft to instance value."""

        validated_data["is_draft"] = False
        instance = super().update(instance=instance, validated_data=validated_data)
        return instance


class CategoryListSerializer(CommonTalentManagementListSerializer):
    """Category model list serializer."""

    class Meta(CommonTalentManagementListSerializer.Meta):
        model = Category
        fields = CommonTalentManagementListSerializer.Meta.fields


class CategoryStatusUpdateSerializer(AppUpdateModelSerializer):
    """Update model serializer to  update the status of category."""

    class Meta(AppUpdateModelSerializer.Meta):
        model = Category
        fields = ["is_active", "is_archive"]
