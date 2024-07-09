from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import UserFavouriteCUDApiViewset

app_name = "user_favourite"
API_URL_PREFIX = "api/v1"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/user/favourite/cud", UserFavouriteCUDApiViewset)

urlpatterns = [] + router.urls
