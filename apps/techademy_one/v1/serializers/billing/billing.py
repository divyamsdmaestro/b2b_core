from rest_framework import serializers

from apps.common.serializers import AppSerializer


class T1BillingSerializer(AppSerializer):
    """Create serializer class for `Tenant`."""

    start_date = serializers.DateField()
    end_date = serializers.DateField()
    tenant_id = serializers.CharField()
