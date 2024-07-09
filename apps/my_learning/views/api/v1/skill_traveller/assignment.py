from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppModelRetrieveAPIViewSet
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import STAssignment
from apps.my_learning.serializers.v1 import UserSTAssignmentListSerializer


class UserSTAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Retrieve api for STAssignment."""

    serializer_class = UserSTAssignmentListSerializer
    queryset = STAssignment.objects.all()

    def get_serializer_context(self):
        """Overriden to add st tracker to serializer context."""

        st_assignment = get_object_or_404(STAssignment, id=self.kwargs["pk"])
        context = super().get_serializer_context()
        if st_assignment.type == CommonLearningAssignmentTypeChoices.final_assignment:
            context["st_tracker"] = st_assignment.skill_traveller.related_user_skill_traveller_trackers.filter(
                user=self.get_user()
            ).first()
        elif st_assignment.type == CommonLearningAssignmentTypeChoices.dependent_assignment:
            context[
                "st_tracker"
            ] = st_assignment.st_course.skill_traveller.related_user_skill_traveller_trackers.filter(
                user=self.get_user()
            ).first()
        return context
