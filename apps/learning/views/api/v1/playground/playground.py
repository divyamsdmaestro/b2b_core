from django_filters import rest_framework as filters
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
from apps.learning.config import PlaygroundGuidanceChoices, PlaygroundTypeChoices, ProficiencyChoices
from apps.learning.helpers import BaseLearningSkillRoleFilter
from apps.learning.models import CategoryRole, CategorySkill, Playground, PlaygroundImage
from apps.learning.serializers.v1 import (
    PlaygroundCUDModelSerializer,
    PlaygroundListModelSerializer,
    PlaygroundRetrieveSerializer,
)

PlaygroundImageUploadAPIView = get_upload_api_view(meta_model=PlaygroundImage, meta_fields=["id", "image"])


class PlaygroundListApiViewSet(
    SortingMixin, CatalogueFilterMixin, FavouriteFilterMixin, UserGroupFilterMixin, AppModelListAPIViewSet
):
    """Api view to list the Playgrounds."""

    class PlaygroundFilter(BaseLearningSkillRoleFilter):
        """Filter class to support multiple choices for `Playground` model."""

        playground_type = filters.MultipleChoiceFilter(
            field_name="playground_type", choices=PlaygroundTypeChoices.choices
        )
        guidance_type = filters.MultipleChoiceFilter(
            field_name="guidance_type", choices=PlaygroundGuidanceChoices.choices
        )

        class Meta(BaseLearningSkillRoleFilter.Meta):
            fields = BaseLearningSkillRoleFilter.Meta.fields + [
                "playground_type",
                "guidance_type",
            ]

    queryset = Playground.objects.alive().order_by("created_at")
    serializer_class = PlaygroundListModelSerializer
    filterset_class = PlaygroundFilter
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
        playground_type = self.serializer_class().serialize_dj_choices(PlaygroundTypeChoices.choices)
        guidance_type = self.serializer_class().serialize_dj_choices(PlaygroundGuidanceChoices.choices)
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
            "playground_type": playground_type,
            "guidance_type": guidance_type,
            "sort_by": get_sorting_meta(sorting_options),
        }
        return self.send_response(data)


class PlaygroundRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve the playground."""

    serializer_class = PlaygroundRetrieveSerializer
    queryset = Playground.objects.alive()


class PlaygroundCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to create, edit & delete the Playgrounds."""

    queryset = Playground.objects.all()
    serializer_class = PlaygroundCUDModelSerializer
