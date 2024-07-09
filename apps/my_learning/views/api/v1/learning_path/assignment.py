from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppModelRetrieveAPIViewSet
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import LPAssignment
from apps.my_learning.serializers.v1 import UserLPAssignmentListSerializer


class UserLPAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Retrieve api for LPAssignment."""

    serializer_class = UserLPAssignmentListSerializer
    queryset = LPAssignment.objects.all()

    def get_serializer_context(self):
        """Overriden to add lp tracker to serializer context."""

        lp_assignment = get_object_or_404(LPAssignment, id=self.kwargs["pk"])
        context = super().get_serializer_context()
        if lp_assignment.type == CommonLearningAssignmentTypeChoices.final_assignment:
            context["lp_tracker"] = lp_assignment.learning_path.related_user_learning_path_trackers.filter(
                user=self.get_user()
            ).first()
        elif lp_assignment.type == CommonLearningAssignmentTypeChoices.dependent_assignment:
            context["lp_tracker"] = lp_assignment.lp_course.learning_path.related_user_learning_path_trackers.filter(
                user=self.get_user()
            ).first()
        return context
