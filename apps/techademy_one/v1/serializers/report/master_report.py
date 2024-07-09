from rest_framework import serializers

from apps.common.serializers import AppSerializer


class T1TenantMasterReportSerializer(AppSerializer):
    """Tenant wise Master Report serializer."""

    tenant_id = serializers.CharField()
    report_name = serializers.CharField()
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)


class T1TenantMasterReportStatusSerializer(AppSerializer):
    """Tenant wise Master Report Status serializer."""

    tenant_id = serializers.CharField()
    report_name = serializers.CharField(required=False, allow_null=True)
    report_id = serializers.CharField(required=False, allow_null=True)

    def validate(self, attrs):
        """Validate if report name or uuid is present."""

        if not attrs.get("report_name") and not attrs.get("report_id"):
            raise serializers.ValidationError({"report_id": "This field is required."})
        return attrs
