from django.db.models import Q
from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import ALPAssessment
from apps.learning.serializers.v1 import ALPAssessmentCUDModelSerializer, ALPAssessmentListModelSerializer


class ALPAssessmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset for alp assessments."""

    queryset = ALPAssessment.objects.all()
    serializer_class = ALPAssessmentCUDModelSerializer


class ALPAssessmentListAPiViewSet(AppModelListAPIViewSet):
    """Api viewset to list alp assessments."""

    serializer_class = ALPAssessmentListModelSerializer
    queryset = ALPAssessment.objects.order_by("sequence", "created_at")
    filterset_fields = [
        "type",
        "alp_lp",
    ]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        return self.send_response(data)

    def get_queryset(self):
        """Overridden to filter the value based on query_params."""

        alp = self.request.query_params.get("alp")
        entire_alp = self.request.query_params.get("entire_alp")
        if alp and entire_alp:
            return self.queryset.filter(Q(alp_lp__advanced_learning_path=alp) | Q(alp=alp))
        elif alp:
            return self.queryset.filter(alp=alp)
        else:
            return self.queryset


class ALPAssessmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Alp assessment retrieve API viewset."""

    serializer_class = ALPAssessmentListModelSerializer
    queryset = ALPAssessment.objects.all()
