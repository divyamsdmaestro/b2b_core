from django.db.models import Q
from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import STAssignment
from apps.learning.serializers.v1 import STAssignmentCUDModelSerializer, STAssignmentListModelSerializer


class STAssignmentListApiViewSet(AppModelListAPIViewSet):
    """List api view for st_course & skill_traveller assignments."""

    serializer_class = STAssignmentListModelSerializer
    queryset = STAssignment.objects.order_by("sequence", "created_at")
    filterset_fields = ["type", "st_course"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        return self.send_response(data)

    def get_queryset(self):
        """Overridden to filter the value based on query_params."""

        skill_traveller = self.request.query_params.get("skill_traveller")
        entire_sta = self.request.query_params.get("entire_sta")
        if skill_traveller and entire_sta:
            return self.queryset.filter(
                Q(st_course__skill_traveller_id=skill_traveller) | Q(skill_traveller_id=skill_traveller)
            )
        elif skill_traveller:
            return self.queryset.filter(skill_traveller_id=skill_traveller)
        else:
            return self.queryset


class STAssignmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """CUD API view for st_course & skill_traveller assignments."""

    serializer_class = STAssignmentCUDModelSerializer
    queryset = STAssignment.objects.all()


class STAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """skill traveller assignment retrieve API viewset."""

    serializer_class = STAssignmentListModelSerializer
    queryset = STAssignment.objects.all()
