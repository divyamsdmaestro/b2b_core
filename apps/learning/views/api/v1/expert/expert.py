from rest_framework.decorators import action

from apps.common.views.api.base import AppAPIView
from apps.common.views.api.generic import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import Expert
from apps.learning.serializers.v1 import ExpertApprovalSerializer, ExpertCUDModelSerializer, ExpertListSerializer
from apps.my_learning.config import ActionChoices


class ExpertCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete experts."""

    serializer_class = ExpertCUDModelSerializer
    queryset = Expert.objects.all()


class ExpertListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list experts."""

    queryset = Expert.objects.all()
    serializer_class = ExpertListSerializer
    filterset_fields = ["action", "course", "learning_path", "advanced_learning_path"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "course__name",
        "learning_path__name",
        "advanced_learning_path__name",
    ]

    def get_queryset(self):
        """Overriden to filter the queryset based on the action."""

        queryset = super().get_queryset()
        action = self.request.query_params.get("action")
        if action and action in [ActionChoices.pending, ActionChoices.rejected]:
            queryset = queryset.exclude(action=ActionChoices.approved)
        return queryset

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        action = self.serializer_class().serialize_dj_choices(ActionChoices.choices)
        return self.send_response(data={"action": action})


class ExpertRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Viewset to retrieve the expert detail."""

    serializer_class = ExpertListSerializer
    queryset = Expert.objects.all()


class ExpertApproveApiView(AppAPIView):
    """Api view to approve the expert."""

    serializer_class = ExpertApprovalSerializer

    def post(self, request, *args, **kwargs):
        """Perform the expert approval."""

        validated_data = self.get_valid_serializer().validated_data
        expert_instance = validated_data["expert"]
        expert_instance.action = validated_data["action"]
        expert_instance.save()
        return self.send_response("Success")
