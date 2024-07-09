from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    CourseAssessmentCUDApiViewSet,
    CourseAssessmentListAPiViewSet,
    CourseAssessmentRetrieveApiViewSet,
    CourseAssignmentCUDApiViewSet,
    CourseAssignmentListApiViewSet,
    CourseAssignmentRetrieveApiViewSet,
    CourseBulkUploadAPIView,
    CourseBulkUploadSampleFileAPIView,
    CourseCloneApiView,
    CourseCUDApiViewSet,
    CourseImageUploadAPIView,
    CourseListApiViewSet,
    CourseModuleCUDApiViewSet,
    CourseModuleListApiViewSet,
    CourseModuleRetrieveApiViewSet,
    CourseModuleSequenceUpdateAPIView,
    CourseResourceApiViewSet,
    CourseResourceListApiViewSet,
    CourseRetrieveApiViewSet,
    CourseSubModuleCUDApiViewSet,
    CourseSubModuleListApiViewSet,
    YakshaAssessmentListApiView,
)

app_name = "course"
API_URL_PREFIX = "api/v1/course"
COURSE_LIST_PREFIX = f"{API_URL_PREFIX}/(?P<course_pk>[^/.]+)"
SUBMODULE_LIST_PREFIX = f"{API_URL_PREFIX}/submodule"

router = AppSimpleRouter()

# Course Api's
router.register(f"{API_URL_PREFIX}/cud", CourseCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", CourseListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", CourseRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/resource/cud", CourseResourceApiViewSet)
router.register(f"{COURSE_LIST_PREFIX}/resource/list", CourseResourceListApiViewSet)

# CourseModule Api's
router.register(f"{API_URL_PREFIX}/module/cud", CourseModuleCUDApiViewSet)
router.register(f"{COURSE_LIST_PREFIX}/module/list", CourseModuleListApiViewSet)
router.register(f"{API_URL_PREFIX}/module/view-detail", CourseModuleRetrieveApiViewSet)

# CourseSubModule Api's
router.register(f"{SUBMODULE_LIST_PREFIX}/cud", CourseSubModuleCUDApiViewSet)
router.register(f"{SUBMODULE_LIST_PREFIX}/list", CourseSubModuleListApiViewSet)
router.register(f"{SUBMODULE_LIST_PREFIX}/list/(?P<module>[^/.]+)", CourseSubModuleListApiViewSet)

# CourseAssessment Api's
router.register(f"{API_URL_PREFIX}/assessment/cud", CourseAssessmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/list", CourseAssessmentListAPiViewSet)
router.register(f"{API_URL_PREFIX}/assessment/view-detail", CourseAssessmentRetrieveApiViewSet)


# CourseAssignment Api's
router.register(f"{API_URL_PREFIX}/assignment/cud", CourseAssignmentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/list", CourseAssignmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/assignment/view-detail", CourseAssignmentRetrieveApiViewSet)


urlpatterns = [
    path(f"{API_URL_PREFIX}/image/upload/", CourseImageUploadAPIView.as_view(), name="course-image-upload"),
    path(f"{API_URL_PREFIX}/clone/", CourseCloneApiView.as_view(), name="course-clone"),
    path(f"{API_URL_PREFIX}/bulk/upload/", CourseBulkUploadAPIView.as_view(), name="course-bulk-upload"),
    path(
        f"{API_URL_PREFIX}/bulk/upload/sample/file/download/",
        CourseBulkUploadSampleFileAPIView.as_view(),
        name="sample-file-download",
    ),
    path("api/v1/yaksha/assessment/list/", YakshaAssessmentListApiView.as_view(), name="yaksha-assessment-list"),
    path(
        f"{API_URL_PREFIX}/module/sequence/update/",
        CourseModuleSequenceUpdateAPIView.as_view(),
        name="module-sequence-update",
    ),
] + router.urls
