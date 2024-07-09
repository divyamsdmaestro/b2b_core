from django.db.models import Q
from rest_framework import serializers

from apps.access.models import User
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppSerializer
from apps.tenant.models import Tenant
from apps.tenant_service.middlewares import set_db_for_router


class T1UserOnboardSerializer(AppSerializer):
    """Create serializer class for tenant `User`."""

    user_id = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    tenant = serializers.CharField()
    techademy_tenant_id = serializers.CharField()
    group_details = serializers.ListSerializer(child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH))

    def validate_tenant(self, tenant):
        """Validate if tenant exists."""

        tenant_obj = Tenant.objects.filter(uuid=tenant).first()
        if not tenant_obj:
            raise serializers.ValidationError("Tenant doesn't exists with this ID.")
        if not tenant_obj.db_router:
            raise serializers.ValidationError("Tenant database is not yet created.")
        self.context["tenant_obj"] = tenant_obj
        return tenant

    def validate(self, attrs):
        """Validate if User already exists."""

        tenant_obj = self.context["tenant_obj"]
        tenant_obj.db_router.add_db_connection()
        set_db_for_router(tenant_obj.db_name)
        user = User.objects.filter(Q(uuid=attrs["user_id"]) | Q(email=attrs["email"])).first()
        if user:
            attrs["is_already_exists"] = True
            attrs["user_obj"] = user
        attrs["tenant_obj"] = tenant_obj
        return attrs
