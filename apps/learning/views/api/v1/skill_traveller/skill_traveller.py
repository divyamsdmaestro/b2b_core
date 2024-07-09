from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from apps.common.helpers import get_sorting_meta
from apps.common.serializers import AppSerializer
from apps.common.views.api import (
    AppAPIView,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    CatalogueFilterMixin,
    CustomQuerysetFilterMixin,
    SortingMixin,
    UserGroupFilterMixin,
    get_upload_api_view,
)
from apps.learning.config import JourneyTypeChoices, SkillTravellerLearningTypeChoices
from apps.learning.helpers import CommonMultipleChoiceFilter
from apps.learning.models import (
    CategorySkill,
    SkillTraveller,
    SkillTravellerCourse,
    SkillTravellerImageModel,
    SkillTravellerResource,
)
from apps.learning.serializers.v1 import (
    SkillTravellerCourseModelListSerializer,
    SkillTravellerCUDModelSerializer,
    SkillTravellerListModelSerializer,
    SkillTravellerResourceCreateModelSerializer,
    SkillTravellerResourceListModelSerializer,
    SkillTravellerRetrieveModelSerializer,
    STCourseAllocationCUDSerializer,
)

SkillTravellerImageUploadAPIView = get_upload_api_view(
    meta_model=SkillTravellerImageModel, meta_fields=["id", "image"]
)


class SkillTravellerCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete skill_travellers."""

    serializer_class = SkillTravellerCUDModelSerializer
    queryset = SkillTraveller.objects.alive()


class SkillTravellerListApiViewSet(
    SortingMixin, CatalogueFilterMixin, UserGroupFilterMixin, CustomQuerysetFilterMixin, AppModelListAPIViewSet
):
    """View to list skill_travellers."""

    class SkillTravellerFilter(CommonMultipleChoiceFilter):
        """Filter class to support multiple choices for `SkillTraveller` model."""

        skill = filters.ModelMultipleChoiceFilter(field_name="skill", queryset=CategorySkill.objects.alive())
        journey_type = filters.MultipleChoiceFilter(field_name="journey_type", choices=JourneyTypeChoices.choices)
        learning_type = filters.MultipleChoiceFilter(
            field_name="learning_type", choices=SkillTravellerLearningTypeChoices.choices
        )

        class Meta(CommonMultipleChoiceFilter.Meta):
            fields = CommonMultipleChoiceFilter.Meta.fields + [
                "skill",
                "journey_type",
                "learning_type",
            ]

    queryset = SkillTraveller.objects.alive().order_by("created_at")
    serializer_class = SkillTravellerListModelSerializer
    filterset_class = SkillTravellerFilter
    user_group_filter_key = "related_learning_catalogues__related_catalogue_relations__user_group__id__in"
    search_fields = ["name", "code"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        journey_type = self.serializer_class().serialize_dj_choices(JourneyTypeChoices.choices)
        learning_type = self.serializer_class().serialize_dj_choices(SkillTravellerLearningTypeChoices.choices)
        sorting_options = self.get_sorting_options(
            {
                "-modified_at": "Accessed Recently",
                "end_date": "Nearing Deadline",
            }
        )
        data = {
            "journey_type": journey_type,
            "learning_type": learning_type,
            "sort_by": get_sorting_meta(sorting_options),
        }
        return self.send_response(data)


class SkillTravellerRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve the skill_traveller."""

    serializer_class = SkillTravellerRetrieveModelSerializer
    queryset = SkillTraveller.objects.alive()


class SkillTravellerCourseListApiViewSet(AppModelListAPIViewSet):
    """View to retrieve the courses in Skill Traveller."""

    serializer_class = SkillTravellerCourseModelListSerializer
    queryset = SkillTravellerCourse.objects.all().order_by("sequence")
    filterset_fields = ["skill_traveller", "sequence"]
    search_fields = ["course__name"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        skill_traveller = self.serializer_class().serialize_for_meta(
            SkillTraveller.objects.alive(), fields=["id", "name"]
        )
        data = {"skill_traveller": skill_traveller}
        return self.send_response(data)


class SkillTravellerCourseCUDApiViewSet(AppModelCUDAPIViewSet):
    """View to update the courses in Skill Traveller."""

    serializer_class = STCourseAllocationCUDSerializer
    queryset = SkillTravellerCourse.objects.all()


class SkillTravellerCloneApiView(AppAPIView):
    """Api view to clone the given SkillTraveller."""

    class _Serializer(AppSerializer):
        """Serializer class for the same."""

        skill_traveller = serializers.PrimaryKeyRelatedField(queryset=SkillTraveller.objects.alive())

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Clone the SkillTraveller logic."""

        serializer = self.get_valid_serializer()
        skill_traveller: SkillTraveller = serializer.validated_data["skill_traveller"]
        clone_details = skill_traveller.clone()
        return self.send_response(data=clone_details)


class SkillTravellerResourceApiViewSet(AppModelCUDAPIViewSet):
    """Api view to upload the resources for SkillTraveller."""

    serializer_class = SkillTravellerResourceCreateModelSerializer
    queryset = SkillTravellerResource.objects.all()

    def get_serializer_context(self):
        """Include the learning type."""

        context = super().get_serializer_context()
        context["learning_type"] = "skill_traveller"
        return context


class SkillTravellerResourceListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the SkillTraveller resources."""

    serializer_class = SkillTravellerResourceListModelSerializer
    queryset = SkillTravellerResource.objects.all()

    def get_queryset(self):
        """Overridden to provide the list of SkillTraveller resources."""

        skill_traveller_pk = self.kwargs.get("skill_traveller_pk", None)
        skill_traveller_instance = get_object_or_404(SkillTraveller, pk=skill_traveller_pk)

        return skill_traveller_instance.related_skill_traveller_resources.all()
