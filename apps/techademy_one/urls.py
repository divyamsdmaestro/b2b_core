from django.urls import path

from ..common.routers import AppSimpleRouter
from .v1 import views as api_v1

V1_API_URL_PREFIX = "api/t1/v1"
app_name = "techademy_one"


router = AppSimpleRouter()
# Log
router.register(f"{V1_API_URL_PREFIX}/tenant/log/list", api_v1.T1EnrollmentListApiViewSet)
# Course
router.register(f"{V1_API_URL_PREFIX}/user/progress/list", api_v1.T1UserCourseListAPIViewSet)
# BadgeActivity
router.register(f"{V1_API_URL_PREFIX}/user/badge/activity/list", api_v1.T1BadgeActivityListApiViewSet)


urlpatterns = [
    # Tenant
    path(f"{V1_API_URL_PREFIX}/tenant/onboard/", api_v1.T1TenantCreationAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/tenant/<uuid:tenant_id>/", api_v1.T1TenantCreationStatusAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/tenant/<uuid:tenant_id>/roles/", api_v1.T1TenantRolesAPIView.as_view()),
    # User
    path(f"{V1_API_URL_PREFIX}/user/onboard/", api_v1.T1UserOnboardAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/bulk/user/onboard/", api_v1.T1BulkUserOnboardAPIView.as_view()),
    # Billing
    path(f"{V1_API_URL_PREFIX}/tenant/billing/", api_v1.T1BillingAPIView.as_view()),
    # Report
    path(f"{V1_API_URL_PREFIX}/tenant/report/", api_v1.T1TenantMasterReportAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/tenant/report/status/", api_v1.T1TenantMasterReportStatusAPIView.as_view()),
    # Course
    path(f"{V1_API_URL_PREFIX}/tenant/courses/", api_v1.T1CourseListAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/top-courses/", api_v1.T1UserTopCourseAPIView.as_view()),
    # My Learning
    path(f"{V1_API_URL_PREFIX}/user/learning-hours/", api_v1.T1UserTotalLearningHourAPIView.as_view()),
] + router.urls
