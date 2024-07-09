from rest_framework import serializers

from apps.common.serializers import AppSerializer


class CustomReportSerializer(AppSerializer):
    """Report serializer."""

    report_name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    report_type = serializers.CharField()

    def validate_report_type(self, report_type):
        """Validate Report Type is valid from the choices."""

        report_type = report_type.lower()
        if report_type.lower() not in ["master", "compliance", "cdp"]:
            raise serializers.ValidationError("Invalid report type. The option must be master, compliance or cdp")
        return report_type


class CustomReportStatusSerializer(AppSerializer):
    """Report Status serializer."""

    report_name = serializers.CharField(required=False, allow_null=True)
    report_id = serializers.CharField(required=False, allow_null=True)

    def validate(self, attrs):
        """Validate if report name or uuid is present."""

        if not attrs.get("report_name") and not attrs.get("report_id"):
            raise serializers.ValidationError({"report_id": "This field is required."})
        return attrs
