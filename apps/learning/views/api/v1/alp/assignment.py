from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import ALPAssignment
from apps.learning.serializers.v1 import ALPAssignmentCUDModelSerializer, ALPAssignmentListModelSerializer


class ALPAssignmentListApiViewSet(AppModelListAPIViewSet):
    """List api view for alp assignments."""

    serializer_class = ALPAssignmentListModelSerializer
    queryset = ALPAssignment.objects.order_by("sequence", "created_at")
    filterset_fields = ["type", "alp_lp", "alp"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        return self.send_response(data)


class ALPAssignmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """CUD API view for alp assignments."""

    serializer_class = ALPAssignmentCUDModelSerializer
    queryset = ALPAssignment.objects.all()


class ALPAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Alp assignment retrieve API viewset."""

    serializer_class = ALPAssignmentListModelSerializer
    queryset = ALPAssignment.objects.all()
