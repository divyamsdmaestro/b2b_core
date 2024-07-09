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
from apps.learning.models import CategorySkill, CategorySkillImageModel
from apps.learning.serializers.v1 import (
    CategorySkillCUDModelSerializer,
    CategorySkillListSerializer,
    CategorySkillStatusUpdateSerializer,
)

CategorySkillImageUploadAPIView = get_upload_api_view(meta_model=CategorySkillImageModel, meta_fields=["id", "image"])


class CategorySkillCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete skill."""

    serializer_class = CategorySkillCUDModelSerializer
    queryset = CategorySkill.objects.alive()


class CategorySkillListApiViewSet(SortingMixin, FavouriteFilterMixin, CatalogueFilterMixin, AppModelListAPIViewSet):
    """Api viewset to retrieve skill."""

    serializer_class = CategorySkillListSerializer
    queryset = CategorySkill.objects.alive().order_by("-no_of_course", "created_at")
    filterset_fields = [
        "category",
        "is_popular",
        "is_recommended",
        "related_courses",
    ]
    search_fields = ["name"]
    all_table_columns = {
        "name": "Skill Name",
        "created_at": "Creation Date",
        "no_of_course": "No. Of Courses",
        "no_of_lp": "No. Of LP",
        "no_of_alp": "No. Of ALP",
        "is_active": "Skill Status",
    }

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Meta for Frontend to sort the list."""

        return self.send_response(data={"sort_by": get_sorting_meta(self.get_default_sorting_options())})


class CategorySkillStatusUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api viewset to update the status of the skill."""

    serializer_class = CategorySkillStatusUpdateSerializer
    queryset = CategorySkill.objects.alive()
