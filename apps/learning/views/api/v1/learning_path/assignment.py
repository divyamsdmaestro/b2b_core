from django.db.models import Q
from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import LPAssignment
from apps.learning.serializers.v1 import LPAssignmentCUDModelSerializer, LPAssignmentListModelSerializer


class LPAssignmentListApiViewSet(AppModelListAPIViewSet):
    """List api view for lp_course & learning_path assignments."""

    serializer_class = LPAssignmentListModelSerializer
    queryset = LPAssignment.objects.order_by("sequence", "created_at")
    filterset_fields = [
        "type",
        "lp_course",
    ]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        return self.send_response(data)

    def get_queryset(self):
        """Overridden to filter the value based on query_params."""

        learning_path = self.request.query_params.get("learning_path")
        entire_lpa = self.request.query_params.get("entire_lpa")
        if learning_path and entire_lpa:
            return self.queryset.filter(Q(lp_course__learning_path=learning_path) | Q(learning_path=learning_path))
        elif learning_path:
            return self.queryset.filter(learning_path=learning_path)
        else:
            return self.queryset


class LPAssignmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """CUD API view for lp_course & learning_path assignments."""

    serializer_class = LPAssignmentCUDModelSerializer
    queryset = LPAssignment.objects.all()


class LPAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Learning path assignment retrieve API viewset."""

    serializer_class = LPAssignmentListModelSerializer
    queryset = LPAssignment.objects.all()
