from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppModelCreateAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import PlaygroundGroup
from apps.my_learning.models.tracker.playground_group import UserPlaygroundGroupTracker
from apps.my_learning.serializers.v1 import (
    UserPlaygroundGroupListSerializer,
    UserPlaygroundGroupRetrieveSerializer,
    UserPlaygroundGroupTrackerCreateSerializer,
    UserPlaygroundRelationListSerializer,
)
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet


class UserPlaygroundGroupListApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """Viewset to list the PlaygroundGroup details."""

    serializer_class = UserPlaygroundGroupListSerializer
    queryset = PlaygroundGroup.objects.unarchived()

    def get_queryset(self):
        """Filter Playground group trackers based on user enrolled."""

        if self.request.query_params.get("enrolled"):
            enrollment_details = UserPlaygroundGroupTracker.objects.filter(user=self.request.user).values_list(
                "playground_group", flat=True
            )
            self.queryset = self.queryset.filter(id__in=enrollment_details)
        return self.get_sorted_queryset()

    def sorting_options(self):
        """Returns the sorting options."""

        return {
            "-related_user_playground_group_trackers__last_accessed_on": "Accessed Recently",
            "related_user_playground_group_trackers__valid_till": "Nearing Deadline",
        }


class UserPlaygroundGroupRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api viewset to retrieve playground"""

    serializer_class = UserPlaygroundGroupRetrieveSerializer
    queryset = PlaygroundGroup.objects.alive()


class UserPGTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """User Playground Group CUD viewset."""

    serializer_class = UserPlaygroundGroupTrackerCreateSerializer
    queryset = UserPlaygroundGroupTracker.objects.all()


class UserPlaygroundRelationListApiViewSet(AppModelListAPIViewSet):
    """Playground relation list api view set."""

    serializer_class = UserPlaygroundRelationListSerializer

    def get_queryset(self):
        """Returns the list of playground based on playground_group."""

        pg = self.kwargs.get("id")
        pg_instance = get_object_or_404(PlaygroundGroup, id=pg)
        return pg_instance.related_playground_relations.all()
