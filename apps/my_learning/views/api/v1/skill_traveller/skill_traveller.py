from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from apps.common.helpers import get_sorting_meta
from apps.common.views.api import (
    AppModelCreateAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    CatalogueFilterMixin,
    FavouriteFilterMixin,
    SortingMixin,
)
from apps.common.views.api.base import AppAPIView
from apps.learning.config import (
    AssessmentTypeChoices,
    CommonLearningAssignmentTypeChoices,
    JourneyTypeChoices,
    SkillTravellerLearningTypeChoices,
)
from apps.learning.models import SkillTraveller
from apps.my_learning.models import UserSkillTravellerTracker
from apps.my_learning.serializers.v1 import (
    UserSkillTravellerCourseListSerializer,
    UserSkillTravellerListSerializer,
    UserSkillTravellerRetrieveSerializer,
    UserSkillTravellerTrackerCreateSerializer,
    UserSTAssessmentListSerializer,
    UserSTAssignmentListSerializer,
)


class UserSkillTravellerListApiViewSet(
    SortingMixin, CatalogueFilterMixin, FavouriteFilterMixin, AppModelListAPIViewSet
):
    """Viewset to list the skill_traveller with enrolled_details.."""

    serializer_class = UserSkillTravellerListSerializer
    queryset = SkillTraveller.objects.unarchived()
    filterset_fields = [
        "created_at",
        "skill",
        "journey_type",
        "learning_type",
        "proficiency",
        "category",
        "is_popular",
        "is_recommended",
        "is_trending",
    ]
    search_fields = ["name", "code"]

    def get_queryset(self):
        """Overridden to filter the queryset based on query params."""

        user = self.get_user()
        user_group = user.related_user_groups.all()
        queryset = super().get_queryset()
        if self.request.query_params.get("overall"):
            queryset = queryset.filter(
                Q(related_learning_catalogues__related_catalogue_relations__user_group__in=user_group)
                | Q(related_learning_catalogues__related_catalogue_relations__user=user)
                | Q(related_enrollments__user=user)
                | Q(related_enrollments__user_group__in=user_group)
            ).distinct()
        return queryset

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        journey_type = self.serializer_class().serialize_dj_choices(JourneyTypeChoices.choices)
        learning_type = self.serializer_class().serialize_dj_choices(SkillTravellerLearningTypeChoices.choices)
        sorting_options = self.get_sorting_options(
            {
                "-related_user_skill_traveller_trackers__last_accessed_on": "Accessed Recently",
                "related_user_skill_traveller_trackers__valid_till": "Nearing Deadline",
            }
        )
        data = {
            "learning_type": learning_type,
            "journey_type": journey_type,
            "sort_by": get_sorting_meta(sorting_options),
        }
        return self.send_response(data)


class UserSkillTravellerRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api viewset to retrieve skill_traveller along with the courses."""

    serializer_class = UserSkillTravellerRetrieveSerializer
    queryset = SkillTraveller.objects.alive()


class UserSTTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """Api view to create skill traveller tracker."""

    serializer_class = UserSkillTravellerTrackerCreateSerializer
    queryset = UserSkillTravellerTracker.objects.all()


class UserSTCourseListApiViewSet(AppModelListAPIViewSet):
    """Skill traveller course list api view set."""

    serializer_class = UserSkillTravellerCourseListSerializer

    def get_queryset(self):
        """Returns the list of courses based on st."""

        st = self.kwargs.get("id")
        st_instance = get_object_or_404(SkillTraveller, id=st)
        return st_instance.related_skill_traveller_courses.filter(course__is_deleted=False).order_by("sequence")


class UserSTFinalEvaluationListApiView(AppAPIView):
    """List api view for skill_traveller final assignments & assessments."""

    def get(self, request, *args, **kwargs):
        """Returns the final assignments & assessments."""

        skill_traveller = get_object_or_404(SkillTraveller, id=kwargs.get("skill_traveller_id"))
        final_assignments = skill_traveller.related_st_assignments.filter(
            type=CommonLearningAssignmentTypeChoices.final_assignment
        ).order_by("sequence", "created_at")
        final_assessments = skill_traveller.related_st_assessments.filter(
            type=AssessmentTypeChoices.final_assessment
        ).order_by("sequence", "created_at")
        context = self.get_serializer_context()
        context["st_tracker"] = skill_traveller.related_user_skill_traveller_trackers.filter(
            user=self.get_user()
        ).first()
        return self.send_response(
            {
                "final_assignments": UserSTAssignmentListSerializer(
                    final_assignments, many=True, context=context
                ).data,
                "final_assessments": UserSTAssessmentListSerializer(
                    final_assessments, many=True, context=context
                ).data,
            }
        )
