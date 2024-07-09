from django_filters import rest_framework as filters
from rest_framework.decorators import action

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.learning.models import PlaygroundGroup, PlaygroundRelationModel
from apps.learning.serializers.v1 import PlaygroundAllocationCUDSerializer, PlaygroundRelationModelRetrieveSerializer


class PlaygroundRelationModelRetrieveApiViewSet(AppModelListAPIViewSet):
    """View to retrieve the playgrounds in playground group."""

    class PlaygroundFilter(filters.FilterSet):
        """Filter the playground based on the Group."""

        playground_group = filters.ModelMultipleChoiceFilter(queryset=PlaygroundGroup.objects.alive())

        class Meta:
            model = PlaygroundRelationModel
            fields = ["playground_group"]

    serializer_class = PlaygroundRelationModelRetrieveSerializer
    queryset = PlaygroundRelationModel.objects.all()
    filterset_class = PlaygroundFilter
    filterset_fields = ["sequence"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        playground_group = self.serializer_class().serialize_for_meta(
            PlaygroundGroup.objects.alive(), fields=["id", "name"]
        )
        data = {"playground_group": playground_group}
        return self.send_response(data)


class PlaygroundRelationCUDApiViewSet(AppModelCUDAPIViewSet):
    """View to update the playgrounds in playground group."""

    queryset = PlaygroundRelationModel.objects.all()
    serializer_class = PlaygroundAllocationCUDSerializer
