from rest_framework import serializers

from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.leaderboard.config import MilestoneChoices
from apps.leaderboard.models import LeaderboardActivity, LeaderboardCompetition, Milestone


class MilestoneCUDModelSerializer(AppWriteOnlyModelSerializer):
    """`Milestone` model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Milestone
        fields = ["name", "points", "is_active"]

    def get_meta(self) -> dict:
        """Get meta & initial values for `Leaderboard`."""

        return {
            "name": self.serialize_dj_choices(MilestoneChoices.choices),
        }


class MilestoneListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `Milestone` model."""

    class Meta:
        model = Milestone
        fields = [
            "id",
            "uuid",
            "name",
            "points",
            "is_active",
            "created_at",
            "modified_at",
        ]


class LeaderboardActivityListSerializer(AppReadOnlyModelSerializer):
    """List & Retrieve serializer for `LeaderboardActivity` model."""

    milestone = MilestoneListSerializer()
    user = SimpleUserReadOnlyModelSerializer()

    class Meta:
        model = LeaderboardActivity
        fields = [
            "id",
            "uuid",
            "user",
            "milestone",
            "points",
            "course",
            "learning_path",
            "learning_type",
            "ccms_id",
            "is_ccms_obj",
            "created_at",
            "modified_at",
        ]


class LeaderboardCompetitionDetailSerializer(AppReadOnlyModelSerializer):
    """Detail serializer for `LeaderboardCompetition` model."""

    class UserLBSerailizer(SimpleUserReadOnlyModelSerializer):
        total_points = serializers.IntegerField(source="total_leaderboard_points", allow_null=True)

        class Meta(SimpleUserReadOnlyModelSerializer.Meta):
            fields = SimpleUserReadOnlyModelSerializer.Meta.fields + ["total_points"]

    user = UserLBSerailizer()
    competitors = UserLBSerailizer(many=True)

    class Meta:
        model = LeaderboardCompetition
        fields = [
            "id",
            "uuid",
            "user",
            "competitors",
        ]
