from apps.access_control.models import Policy, PolicyCategory, RolePermission
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer


class PolicyReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Policy Model Serializer."""

    policy_category = BaseIDNameSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Policy
        fields = [
            "id",
            "name",
            "description",
            "policy_category",
        ]


class PolicyWriteModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for `Policy`."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Policy
        fields = [
            "name",
            "description",
        ]


class PolicyCategoryReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for `PolicyCategory`."""

    policies = PolicyReadOnlyModelSerializer(source="related_policies", many=True, read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = PolicyCategory
        fields = [
            "id",
            "name",
            "policies",
        ]


class RolePermissionWriteModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for `Policy`."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = RolePermission
        fields = [
            "policy",
            "is_creatable",
            "is_viewable",
            "is_editable",
            "is_deletable",
        ]


class RolePermissionReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for `RolePermission`."""

    policy = PolicyReadOnlyModelSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = RolePermission
        fields = [
            "id",
            "policy",
            "is_creatable",
            "is_viewable",
            "is_editable",
            "is_deletable",
        ]
