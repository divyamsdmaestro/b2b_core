from django.urls import path

from ..common.routers import AppSimpleRouter
from .v1 import views as api_v1

V1_API_URL_PREFIX = "api/c/v1"  # Mainly for prolifics tenant. Need to change prefix.
V1_EXT_API_URL_PREFIX = "api/ext/v1"

COURSE_LIST_PREFIX = f"{V1_EXT_API_URL_PREFIX}/course/(?P<course_pk>[^/.]+)"

app_name = "tenant_extension"
router = AppSimpleRouter()

# Course APIs
router.register(f"{V1_EXT_API_URL_PREFIX}/course/list", api_v1.ExtCourseListApiViewSet)
router.register(f"{COURSE_LIST_PREFIX}/module/list", api_v1.ExtCourseModuleListApiViewSet)

urlpatterns = [
    # User
    path(f"{V1_API_URL_PREFIX}/user/onboard/", api_v1.CustomUserOnboardAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/status/update/", api_v1.CustomUserStatusAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/update/", api_v1.CustomUserUpdateAPIView.as_view()),
    # Report
    path(f"{V1_API_URL_PREFIX}/report/", api_v1.CustomReportAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/report/status/", api_v1.CustomReportStatusAPIView.as_view()),
] + router.urls
