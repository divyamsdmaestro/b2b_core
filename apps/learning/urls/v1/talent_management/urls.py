from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    CategoryCUDApiViewSet,
    CategoryImageUploadAPIView,
    CategoryListApiViewSet,
    CategoryRoleCUDApiViewSet,
    CategoryRoleImageUploadAPIView,
    CategoryRoleListApiViewSet,
    CategorySkillCUDApiViewSet,
    CategorySkillImageUploadAPIView,
    CategorySkillListApiViewSet,
)

app_name = "category"
API_URL_PREFIX = "api/v1/category"

router = AppSimpleRouter()

# Category Api's
router.register(f"{API_URL_PREFIX}/cud", CategoryCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", CategoryListApiViewSet)

# CategoryRole Api's
router.register(f"{API_URL_PREFIX}/role/cud", CategoryRoleCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/role/list", CategoryRoleListApiViewSet)

# CategorySkill Api's
router.register(f"{API_URL_PREFIX}/skill/cud", CategorySkillCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/skill/list", CategorySkillListApiViewSet)


urlpatterns = [
    path(
        f"{API_URL_PREFIX}/image/upload/",
        CategoryImageUploadAPIView.as_view(),
        name="category-image-upload",
    ),
    path(
        f"{API_URL_PREFIX}/role/image/upload/",
        CategoryRoleImageUploadAPIView.as_view(),
        name="category-role-image-upload",
    ),
    path(
        f"{API_URL_PREFIX}/skill/image/upload/",
        CategorySkillImageUploadAPIView.as_view(),
        name="category-skill-image-upload",
    ),
] + router.urls
