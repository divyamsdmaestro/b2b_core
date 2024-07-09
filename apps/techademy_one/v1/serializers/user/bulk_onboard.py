from rest_framework import serializers

from apps.common.serializers import AppSerializer
from apps.tenant.models import Tenant


class T1BulkUserOnboardDetailSerializer(AppSerializer):
    """Serializer class for getting user details."""

    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    user_id = serializers.CharField()


class T1BulkUserOnboardSerializer(AppSerializer):
    """Create serializer class for tenant `User`."""

    user_details = T1BulkUserOnboardDetailSerializer(many=True)
    tenant = serializers.CharField()

    def validate(self, attrs):
        """Validate if tenant exists."""

        tenant_obj = Tenant.objects.filter(uuid=attrs["tenant"]).first()
        if not tenant_obj:
            raise serializers.ValidationError("Tenant doesn't exists with this ID.")
        if not tenant_obj.db_router:
            raise serializers.ValidationError("Tenant database is not yet created.")
        attrs["tenant_obj"] = tenant_obj
        return attrs
