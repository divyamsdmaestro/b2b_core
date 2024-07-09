from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    PlaygroundCUDApiViewSet,
    PlaygroundGroupCUDApiViewSet,
    PlaygroundGroupImageUploadAPIView,
    PlaygroundGroupListApiViewSet,
    PlaygroundGroupRetrieveApiViewSet,
    PlaygroundImageUploadAPIView,
    PlaygroundListApiViewSet,
    PlaygroundRelationCUDApiViewSet,
    PlaygroundRelationModelRetrieveApiViewSet,
    PlaygroundRetrieveApiViewSet,
)

app_name = "playground"
API_URL_PREFIX = "api/v1/playground"

router = AppSimpleRouter()

# Playground
router.register(f"{API_URL_PREFIX}/list", PlaygroundListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", PlaygroundRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/cud", PlaygroundCUDApiViewSet)

# Playground Group
router.register(f"{API_URL_PREFIX}/group/list", PlaygroundGroupListApiViewSet)
router.register(f"{API_URL_PREFIX}/group/view-detail", PlaygroundGroupRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/group/cud", PlaygroundGroupCUDApiViewSet)

# Playground Group Relation
router.register(f"{API_URL_PREFIX}/relation/list", PlaygroundRelationModelRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/relation/cud", PlaygroundRelationCUDApiViewSet)

urlpatterns = [
    # Playground
    path(
        f"{API_URL_PREFIX}/image/upload/",
        PlaygroundImageUploadAPIView.as_view(),
        name="playground-image-upload",
    ),
    # Playground Group
    path(
        f"{API_URL_PREFIX}/group/image/upload/",
        PlaygroundGroupImageUploadAPIView.as_view(),
        name="playground-group-image-upload",
    ),
] + router.urls
