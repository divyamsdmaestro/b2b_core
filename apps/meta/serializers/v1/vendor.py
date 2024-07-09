from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.meta.models import Vendor


class VendorCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer Class for Vendor Model CUD"""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Vendor
        fields = ["name", "email", "contact_number"]
