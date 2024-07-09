from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    LearningUpdateCUDApiViewSet,
    LearningUpdateImageUploadAPIView,
    LearningUpdateListApiViewSet,
    LearningUpdateTypeListAPIView,
)

app_name = "learning_update"
API_URL_PREFIX = "api/v1/learning/update"
router = AppSimpleRouter()

# LearningUpdate Api's
router.register(f"{API_URL_PREFIX}/cud", LearningUpdateCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", LearningUpdateListApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/type/list/", LearningUpdateTypeListAPIView.as_view(), name="learning-update-type-list"),
    path(
        f"{API_URL_PREFIX}/image/upload/",
        LearningUpdateImageUploadAPIView.as_view(),
        name="learning-update-image-upload",
    ),
] + router.urls
