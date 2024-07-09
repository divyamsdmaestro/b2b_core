from apps.access_control.fixtures import PolicyChoices
from apps.access_control.models import Policy, PolicyCategory
from apps.access_control.serializers.v1 import (
    PolicyCategoryReadOnlyModelSerializer,
    PolicyReadOnlyModelSerializer,
    PolicyWriteModelSerializer,
)
from apps.common.views.api import AppModelListAPIViewSet, AppModelUpdateAPIViewSet


class PolicyCategoryListAPIView(AppModelListAPIViewSet):
    """View to list down all the `PolicyCategory` along with `Policy`."""

    serializer_class = PolicyCategoryReadOnlyModelSerializer
    get_object_model = PolicyCategory
    queryset = PolicyCategory.objects.all()
    policy_slug = PolicyChoices.user_role_management


class PolicyListAPIView(AppModelListAPIViewSet):
    """View to list down all the `Policy`."""

    serializer_class = PolicyReadOnlyModelSerializer
    get_object_model = Policy
    queryset = Policy.objects.all()
    policy_slug = PolicyChoices.user_role_management


class PolicyUpdateAPIViewSet(AppModelUpdateAPIViewSet):
    """View to handle `Policy` CUD."""

    serializer_class = PolicyWriteModelSerializer
    queryset = Policy.objects.all()
    policy_slug = PolicyChoices.user_role_management
