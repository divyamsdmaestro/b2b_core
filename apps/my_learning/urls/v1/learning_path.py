from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    CCMSLPAssessmentRetrieveApiView,
    LPAssessmentRetrieveApiViewSet,
    LPAssessmentStartApiView,
    LPAssessmentTrackerCreateAPiViewSet,
    LPAYakshaResultApiView,
    UserCCMSLPCourseListApiView,
    UserCCMSLPListApiView,
    UserCCMSLPRetrieveApiView,
    UserLearningPathListApiViewSet,
    UserLearningPathRetrieveApiViewSet,
    UserLearningPathTrackerCreateApiViewSet,
    UserLPAssignmentRetrieveApiViewSet,
    UserLPCourseListApiViewSet,
    UserLPFinalEvaluationListApiView,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/learning-path"
CCMS_API_URL_PREFIX = "api/v1/my-learning/ccms/learning-path"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserLearningPathListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserLearningPathRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserLearningPathTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<id>[^/.]+)/course/list", UserLPCourseListApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/view-detail", LPAssessmentRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/tracker/create", LPAssessmentTrackerCreateAPiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/view-detail", UserLPAssignmentRetrieveApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/assessment/start/<tracker_pk>/", LPAssessmentStartApiView.as_view()),
    path(f"{API_URL_PREFIX}/assessment/result/<tracker_pk>/", LPAYakshaResultApiView.as_view()),
    path(f"{API_URL_PREFIX}/final/evaluations/list/", UserLPFinalEvaluationListApiView.as_view()),
    path(f"{CCMS_API_URL_PREFIX}/list/", UserCCMSLPListApiView.as_view(), name="ccms-lp-list"),
    path(
        f"{CCMS_API_URL_PREFIX}/<uuid:lp_id>/course/list/",
        UserCCMSLPCourseListApiView.as_view(),
        name="ccms-lp-course-list",
    ),
    path(
        f"{CCMS_API_URL_PREFIX}/view-detail/<uuid>/",
        UserCCMSLPRetrieveApiView.as_view(),
        name="ccms-lp-retrieve",
    ),
    path(
        f"{CCMS_API_URL_PREFIX}/assessment/view-detail/<uuid>/",
        CCMSLPAssessmentRetrieveApiView.as_view(),
        name="ccms-lp-assessment-retrieve",
    ),
] + router.urls
