from apps.access_control.config import RoleTypeChoices
from apps.access_control.fixtures import PolicyChoices
from apps.access_control.models import UserGroup
from apps.access_control.serializers.v1 import UserGroupModelSerializer
from apps.common.serializers import AppReadOnlyModelSerializer
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet


class UserGroupListAPIView(AppModelListAPIViewSet):
    """View to list down all the `UserGroup`."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Serializer class for the same view."""

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = UserGroup
            fields = [
                "id",
                "name",
                "group_id",
                "manager_email",
                "members_count",
            ]

    serializer_class = _Serializer
    get_object_model = UserGroup
    queryset = UserGroup.objects.alive()
    policy_slug = PolicyChoices.user_group_management
    user_group_filter_key = "id__in"
    search_fields = ["name", "group_id", "manager__email"]

    def get_queryset(self):
        """Based on user group filter the queryset returned for manager."""

        queryset = super().get_queryset()
        user = self.get_user()
        if not user.current_role or user.current_role.role_type in [RoleTypeChoices.learner, RoleTypeChoices.author]:
            queryset = queryset.none()
        elif user.current_role.role_type == RoleTypeChoices.manager:
            queryset = queryset.filter(id__in=user.related_manager_user_groups.all().values_list("id", flat=True))
        return queryset


class UserGroupCUAPIViewSet(AppModelCUDAPIViewSet):
    """View to handle `UserGroup` CUD."""

    serializer_class = UserGroupModelSerializer
    queryset = UserGroup.objects.alive()
    policy_slug = PolicyChoices.user_group_management
