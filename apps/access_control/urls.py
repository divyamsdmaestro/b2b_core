from ..common.routers import AppSimpleRouter
from .views.api import v1 as api_v1

V1_API_URL_PREFIX = "api/v1/access/control"

app_name = "access_control"

router = AppSimpleRouter()
router.register(f"{V1_API_URL_PREFIX}/policy/list", api_v1.PolicyListAPIView)
router.register(f"{V1_API_URL_PREFIX}/policy/cud", api_v1.PolicyUpdateAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/policy/category/list", api_v1.PolicyCategoryListAPIView)
router.register(f"{V1_API_URL_PREFIX}/user/role/list", api_v1.UserRoleListAPIView)
router.register(f"{V1_API_URL_PREFIX}/user/role/cud", api_v1.UserRoleCUAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/user/group/list", api_v1.UserGroupListAPIView)
router.register(f"{V1_API_URL_PREFIX}/user/group/cud", api_v1.UserGroupCUAPIViewSet)

urlpatterns = [] + router.urls
