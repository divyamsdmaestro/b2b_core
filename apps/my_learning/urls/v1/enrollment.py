from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    EnrolledUserListApiViewSet,
    EnrollmentBulkUploadAPIView,
    EnrollmentBulkUploadSampleFileAPIView,
    EnrollmentListApiViewSet,
    EnrollmentReminderCUDApiViewSet,
    EnrollmentReminderListApiViewSet,
    EnrollmentUpdateApiViewSet,
    UnenrollmentBulkUploadAPIView,
    UnenrollmentBulkUploadSampleFileAPIView,
    UserBulkEnrollApiView,
    UserEnrollmentCreateApiViewSet,
    UserEnrollmentListApiViewSet,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning"

router = AppSimpleRouter()

# Enrollments
router.register(f"{API_URL_PREFIX}/enrollment/cd", UserEnrollmentCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/user/enrollment", UserEnrollmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/enrollment/list", EnrollmentListApiViewSet)
router.register(f"{API_URL_PREFIX}/enrollment/update", EnrollmentUpdateApiViewSet)
router.register(f"{API_URL_PREFIX}/enrolled/user/list", EnrolledUserListApiViewSet)

# Enrollment Reminders
router.register(f"{API_URL_PREFIX}/enrollment/reminder/cud", EnrollmentReminderCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/enrollment/reminder/list", EnrollmentReminderListApiViewSet)

urlpatterns = [
    path("api/v1/enroll/users/", UserBulkEnrollApiView.as_view()),
    path(f"{API_URL_PREFIX}/enrollment/bulkupload/", EnrollmentBulkUploadAPIView.as_view()),
    path(f"{API_URL_PREFIX}/unenrollment/bulkupload/", UnenrollmentBulkUploadAPIView.as_view()),
    path(f"{API_URL_PREFIX}/enrollment/bulkupload/sample/", EnrollmentBulkUploadSampleFileAPIView.as_view()),
    path(f"{API_URL_PREFIX}/unenrollment/bulkupload/sample/", UnenrollmentBulkUploadSampleFileAPIView.as_view()),
] + router.urls
