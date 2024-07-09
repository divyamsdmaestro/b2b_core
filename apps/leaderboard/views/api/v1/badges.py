from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce

from apps.access.models import User
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.common.views.api.base import LoggedInUserMixin
from apps.leaderboard.config import BadgeTypeChoices
from apps.leaderboard.models import Badge, BadgeActivity
from apps.leaderboard.serializers.v1 import (
    BadgeActivityListSerializer,
    BadgeCreateModelSerializer,
    BadgeListSerializer,
    BadgeUpdateModelSerializer,
    UserBadgeListSerializer,
)


class BadgeCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api Viewset to create, update & delete `Badge`."""

    queryset = Badge.objects.alive()

    def get_serializer_class(self):
        """Overriden to select appropriate serializer class based on action."""

        if self.action == "create":
            return BadgeCreateModelSerializer
        return BadgeUpdateModelSerializer


class BadgeListApiViewSet(AppModelListAPIViewSet):
    """Api Viewset to list Badge."""

    queryset = Badge.objects.alive()
    serializer_class = BadgeListSerializer


class BadgeActivityListApiViewSet(LoggedInUserMixin, AppModelListAPIViewSet):
    """Api Viewset to list Badge."""

    queryset = BadgeActivity.objects.all()
    serializer_class = BadgeActivityListSerializer
    search_fields = ["user__email", "user__first_name", "user__last_name", "user__id", "user__uuid"]
    filterset_fields = ["user__email", "user__first_name", "user__last_name", "user__id", "user__uuid"]


class UserBadgeListApiViewSet(AppModelListAPIViewSet):
    """Api Viewset to list Badge."""

    serializer_class = UserBadgeListSerializer
    queryset = (
        User.objects.alive()
        .annotate(
            badges_points=Coalesce(Sum("related_badge_activities__points"), 0),
            video_count=Coalesce(
                Count(
                    "related_badge_activities__badge",
                    filter=Q(related_badge_activities__badge__type=BadgeTypeChoices.video),
                ),
                0,
            ),
            silver_count=Coalesce(
                Count(
                    "related_badge_activities__badge",
                    filter=Q(related_badge_activities__badge__type=BadgeTypeChoices.silver),
                ),
                0,
            ),
            gold_count=Coalesce(
                Count(
                    "related_badge_activities__badge",
                    filter=Q(related_badge_activities__badge__type=BadgeTypeChoices.gold),
                ),
                0,
            ),
            platinum_count=Coalesce(
                Count(
                    "related_badge_activities__badge",
                    filter=Q(related_badge_activities__badge__type=BadgeTypeChoices.platinum),
                ),
                0,
            ),
        )
        .order_by("-badges_points", "created_at")
    )
    filterset_fields = [
        "email",
        "first_name",
        "last_name",
        "id",
        "uuid",
    ]
    search_fields = ["email", "first_name", "last_name", "id", "uuid"]
