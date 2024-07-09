from apps.common.serializers import AppReadOnlyModelSerializer
from apps.dashboard.models import PowerBIDetail


class PowerBIDetailSerializer(AppReadOnlyModelSerializer):
    """Serializer for `PowerBIDetail` model."""

    class Meta:
        model = PowerBIDetail
        fields = [
            "id",
            "uuid",
            "report_id",
            "report_name",
            "embed_url",
            "dataset_id",
            "dataset_workspace_id",
            "web_url",
        ]
