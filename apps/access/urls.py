from django.urls import path

from ..common.routers import AppSimpleRouter
from .views.api import v1 as api_v1
from .views.v1 import CurrentSessionInfoAPIView, LogoutAPIView, RefreshAuthTokenAPIView, TenantInitialDataAPIView

V1_API_URL_PREFIX = "api/v1/access"

app_name = "access"

router = AppSimpleRouter()
router.register(f"{V1_API_URL_PREFIX}/users/list", api_v1.UserListAPIView)
router.register(f"{V1_API_URL_PREFIX}/users/onboard", api_v1.UserCreateAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/user/connection/list", api_v1.UserConnectionListAPIViewSet)

urlpatterns = [
    path(f"{V1_API_URL_PREFIX}/tenant/initial/details/", TenantInitialDataAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/initial/details/", CurrentSessionInfoAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/refresh/", RefreshAuthTokenAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/logout/", LogoutAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/admin/profile/update/", api_v1.AdminProfileUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/admin/profile/update/meta/", api_v1.AdminProfileUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/admin/user/deboard/login/", api_v1.AdminUserDeboardOrLoginDeleteAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/admin/user/roles/update/", api_v1.AdminUserRoleUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/admin/users/groups/update/", api_v1.AdminUserGroupUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/admin/user/password/update/", api_v1.AdminUserPasswordUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/profile/update/", api_v1.UserProfileUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/switch/role/", api_v1.UserRoleSwitchAPIView.as_view()),
    path(
        f"{V1_API_URL_PREFIX}/users/profile/picture/upload/",
        api_v1.UserProfilePictureUploadAPIView.as_view(),
        name="profile-picture-upload",
    ),
    path(f"{V1_API_URL_PREFIX}/users/tc/agree/", api_v1.UserTCAgreeAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/users/area-of-interest/update/", api_v1.UserAreaOfInterestUpdateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/users/area-of-interest/meta/", api_v1.UserAreaOfInterestUpdateMetaAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/users/dashboard/", api_v1.UserDashboardAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/user/connect/", api_v1.UserConnectAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/users/bulkupload/", api_v1.UserBulkUploadAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/users/bulkupload/sample/", api_v1.UserBulkUploadSampleFileAPIView.as_view()),
] + router.urls
