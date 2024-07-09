from apps.access.models import User, UserConnection
from apps.access.serializers.v1.base import SimpleUserReadOnlyModelSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, BaseIDNameSerializer
from apps.common.views.api import AppAPIView
from apps.forum.models import PostLike
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import Enrollment
from apps.my_learning.serializers.v1 import EnrollmentListModelSerializer


class UserFeedPageApiView(AppAPIView):
    """Api view for user feed page to retrieve the activities of user's friends and following."""

    class LikedPostSerializer(AppReadOnlyModelSerializer):
        created_by = SimpleUserReadOnlyModelSerializer(read_only=True)
        post = BaseIDNameSerializer(read_only=True)

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = PostLike
            fields = [
                "post",
                "created_by",
            ]

    def get(self, request, *args, **kwargs):
        """Handle in get."""

        user = self.get_user()
        user_ids = list(User.objects.filter(related_user_connections__followers=user).values_list("id", flat=True))
        if connection_instance := UserConnection.objects.filter(user=user).first():
            user_ids += list(connection_instance.friends.all().values_list("id", flat=True))
        user_enrollments = Enrollment.objects.filter(user_id__in=user_ids, is_enrolled=True).order_by("-created_at")
        return self.send_response(
            {
                "enrolled_learnings": EnrollmentListModelSerializer(
                    user_enrollments.exclude(learning_status=LearningStatusChoices.completed)[:10],
                    many=True,
                    context=self.get_serializer_context(),
                ).data,
                "completed_learnings": EnrollmentListModelSerializer(
                    user_enrollments.filter(learning_status=LearningStatusChoices.completed)[:10],
                    many=True,
                    context=self.get_serializer_context(),
                ).data,
                "liked_posts": self.LikedPostSerializer(
                    PostLike.objects.filter(created_by_id__in=user_ids).order_by("-created_at")[:10], many=True
                ).data,
            }
        )
