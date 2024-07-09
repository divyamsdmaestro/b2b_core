from apps.common.views.api import (
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelUpdateAPIViewSet,
    CatalogueFilterMixin,
    FavouriteFilterMixin,
    get_upload_api_view,
)
from apps.learning.models import Category, CategoryImageModel
from apps.learning.serializers.v1 import (
    CategoryCUDModelSerializer,
    CategoryListSerializer,
    CategoryStatusUpdateSerializer,
)


class CategoryCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete categories"""

    serializer_class = CategoryCUDModelSerializer
    queryset = Category.objects.alive()


class CategoryListApiViewSet(FavouriteFilterMixin, CatalogueFilterMixin, AppModelListAPIViewSet):
    """Api viewset to retrieve categories"""

    serializer_class = CategoryListSerializer
    queryset = Category.objects.alive().order_by("-no_of_course", "created_at")
    filterset_fields = [
        "is_popular",
        "is_recommended",
    ]
    search_fields = ["name"]
    all_table_columns = {
        "name": "Category Name",
        "created_at": "Creation Date",
        "no_of_course": "No. Of Courses",
        "no_of_lp": "No. Of LP",
        "no_of_alp": "No. Of ALP",
        "is_active": "Category Status",
    }


CategoryImageUploadAPIView = get_upload_api_view(meta_model=CategoryImageModel, meta_fields=["id", "image"])


class CategoryStatusUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api viewset to update the status."""

    serializer_class = CategoryStatusUpdateSerializer
    queryset = Category.objects.alive()
