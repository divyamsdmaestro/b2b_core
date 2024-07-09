from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    AnnouncementCUDApiViewSet,
    AnnouncementImageUploadAPIView,
    AnnouncementListApiViewSet,
)

app_name = "announcement"
API_URL_PREFIX = "api/v1/announcement"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/cud", AnnouncementCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", AnnouncementListApiViewSet)

urlpatterns = [
    path(
        f"{API_URL_PREFIX}/image/upload/",
        AnnouncementImageUploadAPIView.as_view(),
        name="announcement-image-upload",
    ),
] + router.urls
