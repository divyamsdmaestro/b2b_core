from django.db.models import Q
from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import STAssessment
from apps.learning.serializers.v1 import STAssessmentCUDModelSerializer, STAssessmentListModelSerializer


class STAssessmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset for skill traveller assessments."""

    queryset = STAssessment.objects.all()
    serializer_class = STAssessmentCUDModelSerializer


class STAssessmentListAPiViewSet(AppModelListAPIViewSet):
    """Api viewset to list skill traveller assessments."""

    serializer_class = STAssessmentListModelSerializer
    queryset = STAssessment.objects.order_by("sequence", "created_at")
    filterset_fields = [
        "type",
        "st_course",
    ]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        return self.send_response(self.serializer_class().get_filter_meta())

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


class STAssessmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """skill traveller assessment retrieve API viewset."""

    serializer_class = STAssessmentListModelSerializer
    queryset = STAssessment.objects.all()
