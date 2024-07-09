from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    UserALPLearningPathListApiViewSet,
    UserALPListModelApiViewSet,
    UserALPRetrieveApiViewSet,
    UserAlpTrackerCreateApiViewSet,
    UserCCMSALPLearningPathListApiView,
    UserCCMSALPListApiView,
    UserCCMSALPRetrieveApiView,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/advanced-learning-path"
CCMS_API_URL_PREFIX = "api/v1/my-learning/ccms/advanced-learning-path"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserALPListModelApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserALPRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserAlpTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<id>[^/.]+)/learning-path/list", UserALPLearningPathListApiViewSet)

urlpatterns = [
    path(f"{CCMS_API_URL_PREFIX}/list/", UserCCMSALPListApiView.as_view(), name="ccms-alp-list"),
    path(
        f"{CCMS_API_URL_PREFIX}/view-detail/<uuid>/",
        UserCCMSALPRetrieveApiView.as_view(),
        name="ccms-alp-retrieve",
    ),
    path(
        f"{CCMS_API_URL_PREFIX}/<uuid:alp_id>/learning-path/list/",
        UserCCMSALPLearningPathListApiView.as_view(),
        name="ccms-alp-lp-list",
    ),
] + router.urls
