from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    AssignmentCUDApiViewSet,
    AssignmentDocumentUploadAPIView,
    AssignmentGroupCUDApiViewSet,
    AssignmentGroupImageUploadAPIView,
    AssignmentGroupListApiViewSet,
    AssignmentGroupRetrieveApiViewSet,
    AssignmentImageUploadAPIView,
    AssignmentListApiViewSet,
    AssignmentRelationCUDApiViewSet,
    AssignmentRelationListApiViewSet,
    AssignmentResourceApiViewSet,
    AssignmentResourceListApiViewSet,
    AssignmentRetrieveApiViewSet,
)

app_name = "assignment"
API_URL_PREFIX = "api/v1/assignment"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/cud", AssignmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", AssignmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", AssignmentRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/resource/cud", AssignmentResourceApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<assignment_pk>[^/.]+)/resource/list", AssignmentResourceListApiViewSet)

# Assignment Group
router.register(f"{API_URL_PREFIX}-group/list", AssignmentGroupListApiViewSet)
router.register(f"{API_URL_PREFIX}-group/view-detail", AssignmentGroupRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}-group/cud", AssignmentGroupCUDApiViewSet)

# Assignment Group Relation
router.register(f"{API_URL_PREFIX}/relation/list", AssignmentRelationListApiViewSet)
router.register(f"{API_URL_PREFIX}/relation/cud", AssignmentRelationCUDApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/image/upload/", AssignmentImageUploadAPIView.as_view()),
    path(f"{API_URL_PREFIX}/document/upload/", AssignmentDocumentUploadAPIView.as_view()),
    path(f"{API_URL_PREFIX}-group/image/upload/", AssignmentGroupImageUploadAPIView.as_view()),
] + router.urls
