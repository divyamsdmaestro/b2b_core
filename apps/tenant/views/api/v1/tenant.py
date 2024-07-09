from rest_framework.generics import get_object_or_404

from apps.common.serializers import AppReadOnlyModelSerializer
from apps.common.views.api import (
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    AppModelUpdateAPIViewSet,
    get_upload_api_view,
)
from apps.tenant.models import Tenant, TenantBanner, TenantConfiguration, TenantDomain, TenantLogo
from apps.tenant.serializers.v1 import (
    TenantConfigurationModelSerializer,
    TenantCreateModelSerializer,
    TenantDomainCUDModelSerializer,
    TenantDomainListModelSerializer,
    TenantRetrieveModelSerializer,
    TenantUpdateModelSerializer,
)


class TenantListAPIViewSet(AppModelListAPIViewSet):
    """View to handle listing of the `Tenant` model."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Serializer class for the same view."""

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = Tenant
            fields = [
                "id",
                "uuid",
                "idp_id",
                "name",
                "tenancy_name",
                "custom_tenant_id",
            ]
            depth = 1

    serializer_class = _Serializer
    queryset = Tenant.objects.active().order_by("-created_at")
    filterset_fields = ["id", "name", "tenancy_name"]
    search_fields = ["name"]


class TenantCUAPIViewSet(AppModelCUDAPIViewSet):
    """View to handle `Tenant` CUD."""

    queryset = Tenant.objects.alive()

    def get_serializer_class(self):
        """Overriden to select appropriate serializer class based on action."""

        if self.action == "create":
            return TenantCreateModelSerializer
        return TenantUpdateModelSerializer


TenantLogoUploadAPIView = get_upload_api_view(meta_model=TenantLogo, meta_fields=["id", "image"])
TenantBannerUploadAPIView = get_upload_api_view(meta_model=TenantBanner, meta_fields=["id", "image"])


class TenantRetrieveAPIViewSet(AppModelRetrieveAPIViewSet):
    """View to handle `Tenant` model retrieve."""

    queryset = Tenant.objects.alive()
    serializer_class = TenantRetrieveModelSerializer


class TenantDomainListModelApiViewSet(AppModelListAPIViewSet):
    """View to handle listing of the `TenantDomain` model."""

    serializer_class = TenantDomainListModelSerializer
    queryset = TenantDomain.objects.alive()

    def get_queryset(self):
        """Overridden to return the domain list based on tenant."""

        tenant_pk = self.kwargs.get("tenant_pk", None)
        tenant_instance = get_object_or_404(Tenant, pk=tenant_pk)
        return tenant_instance.related_tenant_domains.alive()


class TenantDomainCUDApiViewSet(AppModelCUDAPIViewSet):
    """View to handle updating of the `TenantDomain` model."""

    serializer_class = TenantDomainCUDModelSerializer
    queryset = TenantDomain.objects.alive()


class TenantConfigUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """View to handle the update of TenantConfiguration model."""

    queryset = TenantConfiguration.objects.all()
    serializer_class = TenantConfigurationModelSerializer
