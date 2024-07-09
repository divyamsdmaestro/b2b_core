from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    AdvancedLearningPathCUDApiViewSet,
    AdvancedLearningPathImageUploadAPIView,
    AdvancedLearningPathListApiViewSet,
    AdvancedLearningPathResourceApiViewSet,
    AdvancedLearningPathResourceListApiViewSet,
    AdvancedLearningPathRetrieveApiViewSet,
    ALPAssessmentCUDApiViewSet,
    ALPAssessmentListAPiViewSet,
    ALPAssessmentRetrieveApiViewSet,
    ALPAssignmentCUDApiViewSet,
    ALPAssignmentListApiViewSet,
    ALPAssignmentRetrieveApiViewSet,
    ALPLearningPathCUDApiViewSet,
    ALPLearningPathListApiViewSet,
)

app_name = "advanced_learning_path"
API_URL_PREFIX = "api/v1/advanced-learning-path"

router = AppSimpleRouter()

# Advanced learning paths
router.register(f"{API_URL_PREFIX}/cud", AdvancedLearningPathCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", AdvancedLearningPathListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", AdvancedLearningPathRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/learning-path/cud", ALPLearningPathCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/learning-path/list", ALPLearningPathListApiViewSet)
router.register(f"{API_URL_PREFIX}/resource/cud", AdvancedLearningPathResourceApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<alp_pk>[^/.]+)/resource/list", AdvancedLearningPathResourceListApiViewSet)

# assessments
router.register(f"{API_URL_PREFIX}/assessment/cud", ALPAssessmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/list", ALPAssessmentListAPiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/view-detail", ALPAssessmentRetrieveApiViewSet)

# assignments
router.register(f"{API_URL_PREFIX}/assignment/cud", ALPAssignmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/list", ALPAssignmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/view-detail", ALPAssignmentRetrieveApiViewSet)

urlpatterns = [
    # Advanced learning path
    path(
        f"{API_URL_PREFIX}/image/upload/",
        AdvancedLearningPathImageUploadAPIView.as_view(),
        name="advanced-learning-path-image-upload",
    ),
] + router.urls
