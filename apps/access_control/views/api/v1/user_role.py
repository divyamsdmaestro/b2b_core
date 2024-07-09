from apps.access_control.fixtures import PolicyChoices
from apps.access_control.models import UserRole
from apps.access_control.serializers.v1 import (
    RolePermissionReadOnlyModelSerializer,
    UserRoleModelSerializer,
    UserRoleReadOnlyModelSerializer,
)
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.common.views.api.base import NonAuthenticatedAPIMixin


class UserRoleListAPIView(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """View to list down all the `UserRole`."""

    class _Serializer(UserRoleReadOnlyModelSerializer):
        """Serializer class for the same view."""

        role_permissions = RolePermissionReadOnlyModelSerializer(
            source="related_role_permissions", read_only=True, many=True
        )

        class Meta(UserRoleReadOnlyModelSerializer.Meta):
            fields = UserRoleReadOnlyModelSerializer.Meta.fields + [
                "description",
                "role_permissions",
            ]

    serializer_class = _Serializer
    get_object_model = UserRole
    queryset = UserRole.objects.alive()
    policy_slug = PolicyChoices.user_role_management
    search_fields = ["=name"]


class UserRoleCUAPIViewSet(AppModelCUDAPIViewSet):
    """View to handle `UserRole` CUD."""

    serializer_class = UserRoleModelSerializer
    queryset = UserRole.objects.alive()
    policy_slug = PolicyChoices.user_role_management
