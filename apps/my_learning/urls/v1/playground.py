from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    UserPlaygroundListApiViewSet,
    UserPlaygroundRetrieveApiViewSet,
    UserPlaygroundTrackerCreateApiViewSet,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/playground"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserPlaygroundListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserPlaygroundRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserPlaygroundTrackerCreateApiViewSet)

urlpatterns = [] + router.urls
