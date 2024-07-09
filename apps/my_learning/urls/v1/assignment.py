from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    AssignmentReattemptApiView,
    AssignmentSubmissionCreateApiViewSet,
    AssignmentSubmissionListApiViewSet,
    AssignmentSubmissionRetrieveApiViewSet,
    AssignmentSubmissionUpdateApiViewSet,
    SubmissionFileUploadApiView,
    UserAssignmentListApiViewSet,
    UserAssignmentResultApiView,
    UserAssignmentRetrieveApiViewSet,
    UserAssignmentStartApiView,
    UserAssignmentTrackerCreateApiViewSet,
    UserAssignmentTrackerListApiViewSet,
    UserCCMSAssignmentRetrieveApiView,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/assignment"
CCMS_API_URL_PREFIX = "api/v1/my-learning/ccms/assignment"


router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserAssignmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserAssignmentRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/submission/create", AssignmentSubmissionCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/submission/list", AssignmentSubmissionListApiViewSet)
router.register(f"{API_URL_PREFIX}/submission/view-detail", AssignmentSubmissionRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/submission/update", AssignmentSubmissionUpdateApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<assignment_pk>[^/.]+)/tracker/list", UserAssignmentTrackerListApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserAssignmentTrackerCreateApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/<tracker_pk>/file/submission/", SubmissionFileUploadApiView.as_view()),
    path(f"{API_URL_PREFIX}/start/", UserAssignmentStartApiView.as_view()),
    path(f"{API_URL_PREFIX}/<tracker_pk>/calculate/result/", UserAssignmentResultApiView.as_view()),
    path(f"{API_URL_PREFIX}/<tracker_pk>/update/attempt/", AssignmentReattemptApiView.as_view()),
    path(
        f"{CCMS_API_URL_PREFIX}/view-detail/<uuid>/",
        UserCCMSAssignmentRetrieveApiView.as_view(),
        name="ccms-assignment-retrieve",
    ),
] + router.urls
