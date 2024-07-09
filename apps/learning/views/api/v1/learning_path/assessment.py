from django.db.models import Q
from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import LPAssessment
from apps.learning.serializers.v1 import LPAssessmentCUDModelSerializer, LPAssessmentListModelSerializer


class LPAssessmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset for learning path assessments."""

    queryset = LPAssessment.objects.all()
    serializer_class = LPAssessmentCUDModelSerializer


class LPAssessmentListAPiViewSet(AppModelListAPIViewSet):
    """Api viewset to list learning path assessments."""

    serializer_class = LPAssessmentListModelSerializer
    queryset = LPAssessment.objects.order_by("sequence", "created_at")
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


class LPAssessmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Learning path assessment retrieve API viewset."""

    serializer_class = LPAssessmentListModelSerializer
    queryset = LPAssessment.objects.all()
