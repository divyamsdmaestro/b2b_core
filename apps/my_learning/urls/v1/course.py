from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    CAStartApiView,
    CATrackerCreateApiViewSet,
    CAYakshaResultApiView,
    CourseModuleTrackerCreateApiViewSet,
    FileSubmissionReattemptEnableApiView,
    SubModuleFileSubmissionCreateApiViewSet,
    SubModuleFileSubmissionListApiViewSet,
    SubModuleFileSubmissionRetrieveApiViewSet,
    SubModuleFileSubmissionUpdateApiViewSet,
    SubModuleFileUploadApiView,
    SubModuleTrackerCreateApiViewSet,
    SubModuleTrackerRetrieveApiViewSet,
    SubModuleTrackerUpdateApiViewSet,
    UserCatalogueMetaAPIView,
    UserCCMSCourseListApiView,
    UserCCMSCourseModuleListApiView,
    UserCCMSCourseRetrieveApiView,
    UserCCMSCourseSubModuleListApiView,
    UserCourseBookMarkCUDApiViewSet,
    UserCourseBookMarkListApiViewSet,
    UserCourseDetailedRetrieveApiViewSet,
    UserCourseFinalEvaluationListApiView,
    UserCourseListApiViewSet,
    UserCourseMMLVMStartAPIView,
    UserCourseModuleListApiViewSet,
    UserCourseNotesCUDApiViewSet,
    UserCourseNotesListApiViewSet,
    UserCourseSubModuleListApiViewSet,
    UserCourseTrackerCreateApiViewSet,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/course"
CCMS_API_URL_PREFIX = "api/v1/my-learning/ccms/course"

router = AppSimpleRouter()

# courses
router.register(f"{API_URL_PREFIX}/list", UserCourseListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserCourseDetailedRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/tracker/create", UserCourseTrackerCreateApiViewSet)

# module
router.register(f"{API_URL_PREFIX}/(?P<tracker_pk>[^/.]+)/module/list", UserCourseModuleListApiViewSet)
router.register(f"{API_URL_PREFIX}/module/tracker/create", CourseModuleTrackerCreateApiViewSet)

# submodule
router.register(f"{API_URL_PREFIX}/module/(?P<tracker_pk>[^/.]+)/sub-module/list", UserCourseSubModuleListApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/tracker/create", SubModuleTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/tracker/update", SubModuleTrackerUpdateApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/tracker/view-detail", SubModuleTrackerRetrieveApiViewSet)

router.register(f"{API_URL_PREFIX}/sub-module/notes/cud", UserCourseNotesCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/(?P<sub_module_pk>[^/.]+)/notes/list", UserCourseNotesListApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/bookmark/cud", UserCourseBookMarkCUDApiViewSet)
router.register(
    f"{API_URL_PREFIX}/sub-module/(?P<sub_module_pk>[^/.]+)/bookmark/list", UserCourseBookMarkListApiViewSet
)
router.register(f"{API_URL_PREFIX}/sub-module/file/submission/create", SubModuleFileSubmissionCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/file/submission/list", SubModuleFileSubmissionListApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/file/submission/view-detail", SubModuleFileSubmissionRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/sub-module/file/submission/update", SubModuleFileSubmissionUpdateApiViewSet)

# assessments
router.register(f"{API_URL_PREFIX}/assessment/tracker/create", CATrackerCreateApiViewSet)

urlpatterns = [
    path(
        f"{API_URL_PREFIX}/<int:tracker_pk>/lab/start/",
        UserCourseMMLVMStartAPIView.as_view(),
        name="mylearning-course-mmlvm-start",
    ),
    path(f"{API_URL_PREFIX}/assessment/start/<int:tracker_pk>/", CAStartApiView.as_view()),
    path(f"{API_URL_PREFIX}/assessment/result/<int:tracker_pk>/", CAYakshaResultApiView.as_view()),
    path(f"{API_URL_PREFIX}/<int:tracker_pk>/final/evaluations/list/", UserCourseFinalEvaluationListApiView.as_view()),
    # catalogue
    path(f"{API_URL_PREFIX}/catalogue/meta/", UserCatalogueMetaAPIView.as_view()),
    # ccms
    path(f"{CCMS_API_URL_PREFIX}/list/", UserCCMSCourseListApiView.as_view(), name="ccms-course-list"),
    path(
        f"{CCMS_API_URL_PREFIX}/view-detail/<uuid>/",
        UserCCMSCourseRetrieveApiView.as_view(),
        name="ccms-course-retrieve",
    ),
    path(
        f"{CCMS_API_URL_PREFIX}/<int:tracker_pk>/module/list/",
        UserCCMSCourseModuleListApiView.as_view(),
        name="ccms-course-modules-list",
    ),
    path(
        f"{CCMS_API_URL_PREFIX}/module/<int:tracker_pk>/sub-module/list/",
        UserCCMSCourseSubModuleListApiView.as_view(),
        name="ccms-course-submodules-list",
    ),
    path(f"{API_URL_PREFIX}/sub-module/<tracker_pk>/file/upload/", SubModuleFileUploadApiView.as_view()),
    path(f"{API_URL_PREFIX}/sub-module/<tracker_id>/update/attempt/", FileSubmissionReattemptEnableApiView.as_view()),
] + router.urls
