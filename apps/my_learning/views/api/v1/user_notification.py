from django.db.models import Q

from apps.common.views.api.base import AppAPIView
from apps.my_learning.config import ActionChoices
from apps.my_learning.models import Enrollment
from apps.my_learning.serializers.v1 import EnrollmentListModelSerializer


class UserNotificationAPIView(AppAPIView):
    """Api view to get user's recent activity."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        user_enrollments = Enrollment.objects.filter(
            Q(user_group__in=user_groups) | Q(user=user),
            ~Q(action=ActionChoices.pending),
        ).order_by("-created_at")[:10]

        return self.send_response(
            {
                "first_login": not user.data.get("is_tc_agreed", False),
                "user_enrollments": EnrollmentListModelSerializer(
                    user_enrollments, many=True, context=self.get_serializer_context()
                ).data,
            }
        )
