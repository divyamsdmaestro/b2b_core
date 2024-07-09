from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from apps.common.helpers import get_sorting_meta
from apps.common.views.api import (
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    CatalogueFilterMixin,
    CustomQuerysetFilterMixin,
    SortingMixin,
    UserGroupFilterMixin,
    get_upload_api_view,
)
from apps.learning.helpers import AssignmentFilter
from apps.learning.models import Assignment, AssignmentDocument, AssignmentImageModel, AssignmentResource
from apps.learning.serializers.v1 import (
    AssignmentCUDModelSerializer,
    AssignmentListModelSerializer,
    AssignmentResourceCreateModelSerializer,
    AssignmentResourceListModelSerializer,
    AssignmentRetrieveModelSerializer,
)

AssignmentImageUploadAPIView = get_upload_api_view(meta_model=AssignmentImageModel, meta_fields=["id", "image"])

AssignmentDocumentUploadAPIView = get_upload_api_view(meta_model=AssignmentDocument, meta_fields=["id", "file"])


class AssignmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """Assignment CUD api view set."""

    serializer_class = AssignmentCUDModelSerializer
    queryset = Assignment.objects.alive()


class AssignmentListApiViewSet(
    SortingMixin, CatalogueFilterMixin, UserGroupFilterMixin, CustomQuerysetFilterMixin, AppModelListAPIViewSet
):
    """Assignment List API view set."""

    serializer_class = AssignmentListModelSerializer
    queryset = Assignment.objects.alive().order_by("created_at")
    filterset_class = AssignmentFilter
    search_fields = ["name", "code"]
    user_group_filter_key = "related_learning_catalogues__related_catalogue_relations__user_group__id__in"

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        sorting_options = self.get_sorting_options(
            {
                "-modified_at": "Accessed Recently",
                "end_date": "Nearing Deadline",
            }
        )
        data = self.serializer_class().get_filter_meta()
        data["sort_by"] = get_sorting_meta(sorting_options)
        return self.send_response(data)


class AssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Assignment retrieve api view."""

    serializer_class = AssignmentRetrieveModelSerializer
    queryset = Assignment.objects.alive()


class AssignmentResourceApiViewSet(AppModelCUDAPIViewSet):
    """Api view to upload the resources for Assignment."""

    serializer_class = AssignmentResourceCreateModelSerializer
    queryset = AssignmentResource.objects.all()

    def get_serializer_context(self):
        """Include the learning type."""

        context = super().get_serializer_context()
        context["learning_type"] = "assignment"
        return context


class AssignmentResourceListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the Assignment resources."""

    serializer_class = AssignmentResourceListModelSerializer
    queryset = AssignmentResource.objects.all()

    def get_queryset(self):
        """Overridden to provide the list of Assignment resources."""

        assignment_pk = self.kwargs.get("assignment_pk", None)
        assignment_instance = get_object_or_404(Assignment, pk=assignment_pk)

        return assignment_instance.related_assignment_resources.all()
