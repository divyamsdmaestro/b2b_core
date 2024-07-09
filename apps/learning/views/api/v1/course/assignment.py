from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import CourseAssignment
from apps.learning.serializers.v1 import CourseAssignmentCUDModelSerializer, CourseAssignmentListModelSerializer


class CourseAssignmentListApiViewSet(AppModelListAPIViewSet):
    """List api view for course & module assignments."""

    serializer_class = CourseAssignmentListModelSerializer
    queryset = CourseAssignment.objects.order_by("sequence", "created_at")
    filterset_fields = ["type", "course", "module"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        return self.send_response(data)


class CourseAssignmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """CUD API view for course & module assignments."""

    serializer_class = CourseAssignmentCUDModelSerializer
    queryset = CourseAssignment.objects.all()


class CourseAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Course assignment retrieve API viewset."""

    serializer_class = CourseAssignmentListModelSerializer
    queryset = CourseAssignment.objects.all()
