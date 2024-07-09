from apps.common.serializers import BaseIDNameSerializer
from apps.common.views.api.generic import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.meta.models.vendor import Vendor
from apps.meta.serializers.v1 import VendorCUDModelSerializer


class VendorListModelApiViewSet(AppModelListAPIViewSet):
    """Api view to list the vendors."""

    serializer_class = BaseIDNameSerializer
    queryset = Vendor.objects.all()
    search_fields = ["name"]


class VendorCUDModelApiViewset(AppModelCUDAPIViewSet):
    """Api View for Vendor CUD"""

    serializer_class = VendorCUDModelSerializer
    queryset = Vendor.objects.all()
