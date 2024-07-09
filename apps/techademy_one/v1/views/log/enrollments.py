from apps.common.views.api import AppModelListAPIViewSet, NonAuthenticatedAPIMixin
from apps.my_learning.models import Enrollment
from apps.techademy_one.v1.serializers import T1EnrollmentListModelSerializer


class T1EnrollmentListApiViewSet(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """Api view to list assignment submissions."""

    serializer_class = T1EnrollmentListModelSerializer
    queryset = Enrollment.objects.all()
    filterset_fields = ["created_at"]

    def get_queryset(self):
        """Overridden to filter based on given date range."""

        queryset = super().get_queryset()
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        if from_date and to_date:
            return queryset.filter(created_at__date__range=(from_date, to_date))
        return queryset.none()
