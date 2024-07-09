from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.meta.models import Hashtag
from apps.meta.serializers.v1 import HashtagCUDModelSerializer


class HashtagCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete hashtag"""

    serializer_class = HashtagCUDModelSerializer
    queryset = Hashtag.objects.all()


class HashtagListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to retrieve hashtags"""

    queryset = Hashtag.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=Hashtag,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]
