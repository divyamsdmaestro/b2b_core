from rest_framework.decorators import action

from apps.common.helpers import get_sorting_meta
from apps.common.views.api import (
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    CatalogueFilterMixin,
    FavouriteFilterMixin,
    SortingMixin,
    UserGroupFilterMixin,
    get_upload_api_view,
)
from apps.learning.config import ProficiencyChoices
from apps.learning.helpers import BaseLearningSkillRoleFilter
from apps.learning.models import CategoryRole, CategorySkill, PlaygroundGroup, PlaygroundGroupImage
from apps.learning.serializers.v1 import (
    PlaygroundGroupCUDModelSerializer,
    PlaygroundGroupListSerializer,
    PlaygroundGroupRetrieveSerializer,
)

PlaygroundGroupImageUploadAPIView = get_upload_api_view(meta_model=PlaygroundGroupImage, meta_fields=["id", "image"])


class PlaygroundGroupListApiViewSet(
    SortingMixin, CatalogueFilterMixin, FavouriteFilterMixin, UserGroupFilterMixin, AppModelListAPIViewSet
):
    """Api view to list the Playground groups."""

    serializer_class = PlaygroundGroupListSerializer
    queryset = PlaygroundGroup.objects.alive().order_by("created_at")
    filterset_class = BaseLearningSkillRoleFilter
    search_fields = ["name", "code"]
    user_group_filter_key = "related_learning_catalogues__related_catalogue_relations__user_group__id__in"
    all_table_columns = {
        "name": "Name",
        "code": "Code",
        "category": "Category",
        "proficiency": "Proficiency",
        "duration": "Duration",
        "created_by": "Created By",
        "is_active": "Status",
    }

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        skill = self.serializer_class().serialize_for_meta(CategorySkill.objects.alive(), fields=["id", "name"])
        role = self.serializer_class().serialize_for_meta(CategoryRole.objects.alive(), fields=["id", "name"])
        proficiency = self.serializer_class().serialize_dj_choices(ProficiencyChoices.choices)
        sorting_options = self.get_sorting_options(
            {
                "-modified_at": "Accessed Recently",
                "end_date": "Nearing Deadline",
            }
        )
        data = {
            "skill": skill,
            "role": role,
            "proficiency": proficiency,
            "sort_by": get_sorting_meta(sorting_options),
        }
        return self.send_response(data)


class PlaygroundGroupRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve the playground."""

    serializer_class = PlaygroundGroupRetrieveSerializer
    queryset = PlaygroundGroup.objects.alive()


class PlaygroundGroupCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to create, edit & delete the Playground groups."""

    queryset = PlaygroundGroup.objects.all()
    serializer_class = PlaygroundGroupCUDModelSerializer
