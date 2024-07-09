from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    STAssessmentRetrieveApiViewSet,
    STAssessmentStartApiView,
    STAssessmentTrackerCreateApiView,
    STAYakshaResultApiView,
    UserSkillTravellerListApiViewSet,
    UserSkillTravellerRetrieveApiViewSet,
    UserSTAssignmentRetrieveApiViewSet,
    UserSTCourseListApiViewSet,
    UserSTFinalEvaluationListApiView,
    UserSTTrackerCreateApiViewSet,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/skill-traveller"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserSkillTravellerListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserSkillTravellerRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserSTTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<id>[^/.]+)/course/list", UserSTCourseListApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/view-detail", STAssessmentRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/view-detail", UserSTAssignmentRetrieveApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/assessment/<st_assessment>/tracker/create/", STAssessmentTrackerCreateApiView.as_view()),
    path(f"{API_URL_PREFIX}/assessment/start/<tracker_pk>/", STAssessmentStartApiView.as_view()),
    path(f"{API_URL_PREFIX}/assessment/result/<tracker_pk>/", STAYakshaResultApiView.as_view()),
    path(f"{API_URL_PREFIX}/<skill_traveller_id>/final/evaluations/list/", UserSTFinalEvaluationListApiView.as_view()),
] + router.urls
