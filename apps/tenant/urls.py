from django.urls import path

from ..common.routers import AppSimpleRouter
from .views.api import v1 as api_v1

V1_API_URL_PREFIX = "api/v1/tenants"
V1_API_TENANT_PREFIX = r"api/v1/tenants/(?P<tenant_pk>[^/.]+)"

app_name = "tenant"

router = AppSimpleRouter()
router.register(f"{V1_API_URL_PREFIX}/list", api_v1.TenantListAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/detail", api_v1.TenantRetrieveAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/cud", api_v1.TenantCUAPIViewSet)
router.register(f"{V1_API_TENANT_PREFIX}/domain/list", api_v1.TenantDomainListModelApiViewSet)
router.register(f"{V1_API_URL_PREFIX}/domain/cud", api_v1.TenantDomainCUDApiViewSet)
router.register(f"{V1_API_URL_PREFIX}/config/update", api_v1.TenantConfigUpdateApiViewSet)

urlpatterns = [
    path(f"{V1_API_URL_PREFIX}/logo/upload/", api_v1.TenantLogoUploadAPIView.as_view(), name="tenant-logo-upload"),
    path(
        f"{V1_API_URL_PREFIX}/banner/upload/", api_v1.TenantBannerUploadAPIView.as_view(), name="tenant-banner-upload"
    ),
] + router.urls
