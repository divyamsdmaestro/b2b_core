from rest_framework import serializers

from apps.access_control.config import RoleTypeChoices
from apps.access_control.models import RolePermission, UserRole
from apps.access_control.serializers.v1 import (
    RolePermissionReadOnlyModelSerializer,
    RolePermissionWriteModelSerializer,
)
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer


class UserRoleReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for `UserRole`."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserRole
        fields = [
            "id",
            "name",
            "role_type",
        ]


class UserRoleModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for `UserRole` model."""

    role_permissions = RolePermissionWriteModelSerializer(many=True, required=True, write_only=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserRole
        fields = ["name", "description", "role_type", "role_permissions"]

    def validate_role_permissions(self, role_permissions):
        """Validated if its empty."""

        if not role_permissions:
            raise serializers.ValidationError("This Field is required.")
        return role_permissions

    def create(self, validated_data):
        """Handle role_permissions logic."""

        role_permissions = validated_data.pop("role_permissions")
        instance = super().create(validated_data)
        role_permissions_list = [RolePermission(role=instance, **item) for item in role_permissions]
        instance.related_role_permissions.bulk_create(role_permissions_list)
        return instance

    def update(self, instance, validated_data):
        """Handle role_permissions logic."""

        role_permissions = validated_data.pop("role_permissions")
        instance = super().update(instance, validated_data)
        for role_permission in role_permissions:
            policy = role_permission.pop("policy")
            RolePermission.objects.update_or_create(role=instance, policy=policy, defaults=dict(role_permission))
        return instance

    def get_meta(self) -> dict:
        """get meta and initial values."""

        return {
            "role_type": self.serialize_dj_choices(RoleTypeChoices.choices),
        }

    def get_meta_for_update(self, *args, **kwargs):
        """Overriden to add initial data of Role permissions."""

        data = super().get_meta_for_update()

        data["initial"].update(
            {
                "role_permissions": RolePermissionReadOnlyModelSerializer(
                    self.instance.related_role_permissions.all(), many=True
                ).data
            }
        )
        return data
