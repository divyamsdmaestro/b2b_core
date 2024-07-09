from rest_framework.decorators import action

from apps.common.helpers import get_sorting_meta
from apps.common.views.api import (
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelUpdateAPIViewSet,
    CatalogueFilterMixin,
    FavouriteFilterMixin,
    SortingMixin,
    get_upload_api_view,
)
from apps.learning.models import CategoryRole, CategoryRoleImageModel, RoleSkillRelation
from apps.learning.serializers.v1 import (
    CategoryRoleCUDModelSerializer,
    CategoryRoleListSerializer,
    CategoryRoleStatusUpdateSerializer,
)
from apps.learning.validators import draft_action

CategoryRoleImageUploadAPIView = get_upload_api_view(meta_model=CategoryRoleImageModel, meta_fields=["id", "image"])


class CategoryRoleCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete role."""

    queryset = CategoryRole.objects.alive()
    serializer_class = CategoryRoleCUDModelSerializer

    def create(self, request, *args, **kwargs):
        """Overridden to create a role."""

        serializer = CategoryRoleCUDModelSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data = draft_action(validated_data)
        skill_args = validated_data.pop("skill_detail") or []
        instance = serializer.create(validated_data=validated_data)
        skill_relation_instance = [RoleSkillRelation(role=instance, **item) for item in skill_args]
        RoleSkillRelation.objects.bulk_create(skill_relation_instance)
        return self.send_response("success")


class CategoryRoleListApiViewSet(SortingMixin, FavouriteFilterMixin, CatalogueFilterMixin, AppModelListAPIViewSet):
    """Api viewset to retrieve role."""

    serializer_class = CategoryRoleListSerializer
    queryset = CategoryRole.objects.alive().order_by("-no_of_course", "created_at")
    filterset_fields = [
        "category",
        "is_popular",
        "is_recommended",
    ]
    search_fields = ["name"]
    all_table_columns = {
        "name": "Role Name",
        "created_at": "Creation Date",
        "no_of_course": "No. Of Courses",
        "no_of_lp": "No. Of LP",
        "no_of_alp": "No. Of ALP",
        "is_active": "Role Status",
    }

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Meta for Frontend to sort the list."""

        return self.send_response(data={"sort_by": get_sorting_meta(self.get_default_sorting_options())})


class CategoryRoleStatusUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api viewset to update the status of the role."""

    serializer_class = CategoryRoleStatusUpdateSerializer
    queryset = CategoryRole.objects.alive()
