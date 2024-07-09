from django.db.models import Q
from rest_framework import serializers

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppSerializer
from apps.tenant.models import Tenant


class T1TenantAddressCreateSerializer(AppSerializer):
    """Serializer class for T1 Tenant Address model CUD."""

    id = serializers.CharField(required=False, allow_null=True)
    address_line_one = serializers.CharField(required=False, allow_null=True)
    address_line_two = serializers.CharField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True)
    state = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    pincode = serializers.CharField(required=False, allow_null=True)


class T1TenantAdminCreateSerializer(AppSerializer):
    """Serializer class for T1 Tenant Address model CUD."""

    user_id = serializers.CharField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)
    email = serializers.CharField(required=False, allow_null=True)
    contact_number = serializers.CharField(required=False, allow_null=True)


class T1TenantCreateSerializer(AppSerializer):
    """Create serializer class for `Tenant`."""

    tenant_id = serializers.CharField()
    displayName = serializers.CharField()
    tenantName = serializers.CharField()
    tenantEmail = serializers.CharField()
    issuer_url = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    address = T1TenantAddressCreateSerializer(read_only=False, required=False, allow_null=True)
    tenantAdmin = T1TenantAdminCreateSerializer(many=True, read_only=False, required=False, allow_null=True)

    def validate(self, attrs):
        """
        Validate if the tenant already exists with the given `tenancy_name`.
        As directed by @Ayushman (IIHT). These Validations are not
        required instead just return already created.
        """

        name, tenancy_name, tenant_id = attrs["displayName"], attrs["tenantName"], attrs["tenant_id"]
        tenant = Tenant.objects.filter(Q(name=name) | Q(tenancy_name=tenancy_name) | Q(uuid=tenant_id)).first()
        if not tenant:
            return attrs
        attrs["is_tenant_exists"] = True
        return attrs
