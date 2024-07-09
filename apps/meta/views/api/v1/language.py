from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.meta.models import Language
from apps.meta.serializers.v1 import LanguageCUDModelSerializer


class LanguageCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete language"""

    serializer_class = LanguageCUDModelSerializer
    queryset = Language.objects.all()


class LanguageListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to retrieve languages"""

    queryset = Language.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=Language,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]
