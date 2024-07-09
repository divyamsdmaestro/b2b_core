from apps.common.views.api import AppModelCUDAPIViewSet
from apps.my_learning.models import UserFavourite
from apps.my_learning.serializers.v1 import UserFavouriteSerializer


class UserFavouriteCUDApiViewset(AppModelCUDAPIViewSet):
    """ApiViewset to add learning related models to favourite."""

    serializer_class = UserFavouriteSerializer
    queryset = UserFavourite.objects.all()
