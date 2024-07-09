from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    LearningPathCloneApiView,
    LearningPathCUDApiViewSet,
    LearningPathImageUploadAPIView,
    LearningPathListApiViewSet,
    LearningPathResourceApiViewSet,
    LearningPathResourceListApiViewSet,
    LearningPathRetrieveApiViewSet,
    LPAssessmentCUDApiViewSet,
    LPAssessmentListAPiViewSet,
    LPAssessmentRetrieveApiViewSet,
    LPAssignmentCUDApiViewSet,
    LPAssignmentListApiViewSet,
    LPAssignmentRetrieveApiViewSet,
    LPCourseAllocationCUDApiViewSet,
    LPCourseListApiViewSet,
)

app_name = "learning_path"
API_URL_PREFIX = "api/v1/learning-path"

router = AppSimpleRouter()

# Learning paths
router.register(f"{API_URL_PREFIX}/cud", LearningPathCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", LearningPathListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", LearningPathRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/course/list", LPCourseListApiViewSet)
router.register(f"{API_URL_PREFIX}/course/cud", LPCourseAllocationCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/resource/cud", LearningPathResourceApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<learning_path_pk>[^/.]+)/resource/list", LearningPathResourceListApiViewSet)

# assessments
router.register(f"{API_URL_PREFIX}/assessment/cud", LPAssessmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/list", LPAssessmentListAPiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/view-detail", LPAssessmentRetrieveApiViewSet)

# assignments
router.register(f"{API_URL_PREFIX}/assignment/cud", LPAssignmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/list", LPAssignmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/view-detail", LPAssignmentRetrieveApiViewSet)

urlpatterns = [
    path(
        f"{API_URL_PREFIX}/image/upload/",
        LearningPathImageUploadAPIView.as_view(),
        name="learning-path-image-upload",
    ),
    path(f"{API_URL_PREFIX}/clone/", LearningPathCloneApiView.as_view(), name="learning-path-clone"),
] + router.urls
