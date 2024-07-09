from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    UserAssignmentGroupListApiViewSet,
    UserAssignmentGroupRetrieveApiViewSet,
    UserAssignmentGroupTrackerCreateApiViewSet,
    UserAssignmentRelationListApiViewSet,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/assignment-group"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserAssignmentGroupListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserAssignmentGroupRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserAssignmentGroupTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<id>[^/.]+)/assignment/list", UserAssignmentRelationListApiViewSet)

urlpatterns = [] + router.urls
