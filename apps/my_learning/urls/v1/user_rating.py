from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import UserRatingCUDApiViewSet

app_name = "user_rating"
API_URL_PREFIX = "api/v1"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/user/rating/cud", UserRatingCUDApiViewSet)

urlpatterns = [] + router.urls
