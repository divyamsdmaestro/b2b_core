from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    SkillTravellerCloneApiView,
    SkillTravellerCourseCUDApiViewSet,
    SkillTravellerCourseListApiViewSet,
    SkillTravellerCUDApiViewSet,
    SkillTravellerImageUploadAPIView,
    SkillTravellerListApiViewSet,
    SkillTravellerResourceApiViewSet,
    SkillTravellerResourceListApiViewSet,
    SkillTravellerRetrieveApiViewSet,
    STAssessmentCUDApiViewSet,
    STAssessmentListAPiViewSet,
    STAssessmentRetrieveApiViewSet,
    STAssignmentCUDApiViewSet,
    STAssignmentListApiViewSet,
    STAssignmentRetrieveApiViewSet,
)

app_name = "skill_traveller"
API_URL_PREFIX = "api/v1/skill-traveller"

router = AppSimpleRouter()


# Skill traveller
router.register(f"{API_URL_PREFIX}/cud", SkillTravellerCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", SkillTravellerListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", SkillTravellerRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/course/cud", SkillTravellerCourseCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/course/list", SkillTravellerCourseListApiViewSet)
router.register(f"{API_URL_PREFIX}/resource/cud", SkillTravellerResourceApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<skill_traveller_pk>[^/.]+)/resource/list", SkillTravellerResourceListApiViewSet)

# assessments
router.register(f"{API_URL_PREFIX}/assessment/cud", STAssessmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/list", STAssessmentListAPiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/view-detail", STAssessmentRetrieveApiViewSet)

# assignments
router.register(f"{API_URL_PREFIX}/assignment/cud", STAssignmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/list", STAssignmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/view-detail", STAssignmentRetrieveApiViewSet)

urlpatterns = [
    # Skill Traveller
    path(
        f"{API_URL_PREFIX}/image/upload/",
        SkillTravellerImageUploadAPIView.as_view(),
        name="skill-traveller-image-upload",
    ),
    path(f"{API_URL_PREFIX}/clone/", SkillTravellerCloneApiView.as_view(), name="skill-traveller-clone"),
] + router.urls
