from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    UserPGTrackerCreateApiViewSet,
    UserPlaygroundGroupListApiViewSet,
    UserPlaygroundGroupRetrieveApiViewSet,
    UserPlaygroundRelationListApiViewSet,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/playground-group"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserPlaygroundGroupListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserPlaygroundGroupRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserPGTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<id>[^/.]+)/playground/list", UserPlaygroundRelationListApiViewSet)

urlpatterns = [] + router.urls
