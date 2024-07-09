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
from apps.learning.helpers import BaseLearningSkillRoleFilter
from apps.learning.models import AssignmentGroup, AssignmentGroupImageModel, AssignmentRelation
from apps.learning.serializers.v1 import (
    AssignmentAllocationCUDSerializer,
    AssignmentGroupCUDModelSerializer,
    AssignmentGroupListSerializer,
    AssignmentGroupRetrieveSerializer,
    AssignmentRelationListSerializer,
)

AssignmentGroupImageUploadAPIView = get_upload_api_view(
    meta_model=AssignmentGroupImageModel, meta_fields=["id", "image"]
)


class AssignmentGroupListApiViewSet(
    SortingMixin, UserGroupFilterMixin, CatalogueFilterMixin, CustomQuerysetFilterMixin, AppModelListAPIViewSet
):
    """Api view to list the Assignment groups."""

    serializer_class = AssignmentGroupListSerializer
    queryset = AssignmentGroup.objects.alive().order_by("created_at")
    filterset_class = BaseLearningSkillRoleFilter
    search_fields = ["name", "code"]


class AssignmentGroupRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve the assignment."""

    serializer_class = AssignmentGroupRetrieveSerializer
    queryset = AssignmentGroup.objects.alive()


class AssignmentGroupCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to create, edit & delete the Assignment groups."""

    queryset = AssignmentGroup.objects.all()
    serializer_class = AssignmentGroupCUDModelSerializer


class AssignmentRelationListApiViewSet(AppModelListAPIViewSet):
    """View to list the assignments in assignment group."""

    serializer_class = AssignmentRelationListSerializer
    queryset = AssignmentRelation.objects.all().order_by("sequence")
    filterset_fields = ["assignment_group"]


class AssignmentRelationCUDApiViewSet(AppModelCUDAPIViewSet):
    """View to update the assignments in assignment group."""

    queryset = AssignmentRelation.objects.all()
    serializer_class = AssignmentAllocationCUDSerializer
