from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppModelCreateAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import AssignmentGroup, AssignmentRelation
from apps.my_learning.models.tracker.assignment_group import AssignmentGroupTracker
from apps.my_learning.serializers.v1 import (
    UserAssignmentGroupListSerializer,
    UserAssignmentGroupRetrieveSerializer,
    UserAssignmentGroupTrackerCreateSerializer,
    UserAssignmentRelationListSerializer,
)
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet


class UserAssignmentGroupListApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """Viewset to list the AssignmentGroup details."""

    serializer_class = UserAssignmentGroupListSerializer
    queryset = AssignmentGroup.objects.unarchived()


class UserAssignmentGroupRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api viewset to retrieve assignment"""

    serializer_class = UserAssignmentGroupRetrieveSerializer
    queryset = AssignmentGroup.objects.alive()


class UserAssignmentGroupTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """User Assignment Group CUD viewset."""

    serializer_class = UserAssignmentGroupTrackerCreateSerializer
    queryset = AssignmentGroupTracker.objects.all()


class UserAssignmentRelationListApiViewSet(AppModelListAPIViewSet):
    """Assignment relation list api view set."""

    serializer_class = UserAssignmentRelationListSerializer
    queryset = AssignmentRelation.objects.all()

    def get_queryset(self):
        """Returns the list of assignment based on assignment_group."""

        id = self.kwargs.get("id")
        assignment_group = get_object_or_404(AssignmentGroup, id=id)
        return assignment_group.related_assignment_relations.filter(assignment__is_deleted=False).order_by("sequence")
