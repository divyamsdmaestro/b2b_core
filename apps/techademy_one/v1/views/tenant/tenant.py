from django.db.models import F
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.access_control.models import UserRole
from apps.common.views.api import AppAPIView, NonAuthenticatedAPIMixin
from apps.techademy_one.v1.serializers import T1TenantCreateSerializer
from apps.techademy_one.v1.tasks import T1TenantSetupTask
from apps.tenant.models import Tenant
from apps.tenant_service.middlewares import set_db_for_router
from config import settings


class T1TenantCreationAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to create Tenant."""

    serializer_class = T1TenantCreateSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same. On 11-01-24 as per Ayushman (IIHT). For default tenant just send back UUID."""

        if request.data.get("tenant_type") == "master":
            set_db_for_router()
            return self.send_response(
                data={
                    "tenant_id": Tenant.objects.get(tenancy_name=settings.APP_DEFAULT_TENANT_NAME).uuid,
                    "message": "Tenant already created.",
                }
            )

        validated_data = self.get_valid_serializer().validated_data
        tenant_id = validated_data.pop("tenant_id")
        if validated_data.get("is_tenant_exists"):
            return self.send_response(
                data={
                    "tenant_id": tenant_id,
                    "message": "Tenant already created.",
                }
            )
        issuer_url = validated_data.pop("issuer_url")
        display_name = validated_data.pop("displayName")
        tenancy_name = validated_data.pop("tenantName")
        tenant_email = validated_data.pop("tenantEmail")
        tenant = Tenant.objects.create(
            uuid=tenant_id,
            name=display_name,
            tenancy_name=tenancy_name,
            email=tenant_email,
            is_keycloak=True,
            issuer_url=issuer_url,
        )
        tenant.data["tenant_setup_data"] = validated_data
        tenant.save()
        T1TenantSetupTask().run_task(tenant_id=tenant.id)

        # TODO: Authentication, super admin details integration.

        return self.send_response(
            data={
                "tenant_id": tenant.uuid,
                "message": "Tenant created Partially.",
            }
        )


class T1TenantCreationStatusAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to check Tenant creation status."""

    def post(self, request, tenant_id):
        """Logic for the same."""

        # TODO: Authentication, super admin details integration.
        tenant = get_object_or_404(Tenant, uuid=tenant_id)
        return self.send_response(data={"status": tenant.db_status_label})


class T1TenantRolesAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to list Tenant roles."""

    def get(self, request, tenant_id):
        """Logic for the same."""

        # TODO: Authentication, super admin details integration.
        tenant: Tenant = get_object_or_404(Tenant, uuid=tenant_id)
        router = tenant.db_router
        if not router:
            return self.send_error_response(data={"message": "Database is not ready yet."})
        router.add_db_connection()
        set_db_for_router(router.database_name)
        roles = UserRole.objects.all().annotate(role_name=F("name")).values("role_name", "description")
        return Response(roles, status=status.HTTP_200_OK)
