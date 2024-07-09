from apps.common.views.api import AppModelCUDAPIViewSet
from apps.my_learning.models import UserRating
from apps.my_learning.serializers.v1 import UserRatingCUDSerializer


class UserRatingCUDApiViewSet(AppModelCUDAPIViewSet):
    """ApiViewSet to add learning related models to Ratings."""

    serializer_class = UserRatingCUDSerializer
    queryset = UserRating.objects.all()
