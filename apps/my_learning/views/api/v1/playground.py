from apps.common.views.api import AppModelCreateAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import Playground
from apps.my_learning.models.tracker.playground import UserPlaygroundTracker
from apps.my_learning.serializers.v1 import (
    UserPlaygroundListSerializer,
    UserPlaygroundRetrieveSerializer,
    UserPlaygroundTrackerCreateSerializer,
)
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet


class UserPlaygroundListApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """Viewset to list the PlaygroundTrackingModel details."""

    serializer_class = UserPlaygroundListSerializer
    queryset = Playground.objects.unarchived()
    filterset_fields = BaseMyLearningSkillRoleListApiViewSet.filterset_fields + [
        "playground_type",
        "guidance_type",
        "tool",
    ]
    search_fields = ["name", "code"]

    def get_queryset(self):
        """Filter Playground Trackers based on user enrolled."""

        if self.request.query_params.get("enrolled"):
            enrollment_details = UserPlaygroundTracker.objects.filter(user=self.request.user).values("playground")
            self.queryset = self.queryset.filter(id__in=enrollment_details)
        return self.get_sorted_queryset()

    def sorting_options(self):
        """Returns the sorting options."""

        return {
            "-related_user_playground_trackers__last_accessed_on": "Accessed Recently",
            "related_user_playground_trackers__valid_till": "Nearing Deadline",
        }


class UserPlaygroundRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api viewset to retrieve playground"""

    serializer_class = UserPlaygroundRetrieveSerializer
    queryset = Playground.objects.alive()


class UserPlaygroundTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """User Playground CUD viewset."""

    serializer_class = UserPlaygroundTrackerCreateSerializer
    queryset = UserPlaygroundTracker.objects.all()
