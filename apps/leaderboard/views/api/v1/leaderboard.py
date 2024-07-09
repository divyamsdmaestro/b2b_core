from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import serializers
from rest_framework.decorators import action

from apps.access.models import User
from apps.access.serializers.v1 import UserProfilePictureRetrieveSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.event.config import TimePeriodChoices
from apps.leaderboard.models import LeaderboardActivity, LeaderboardCompetition, Milestone
from apps.leaderboard.serializers.v1 import (
    LeaderboardActivityListSerializer,
    LeaderboardCompetitionDetailSerializer,
    MilestoneCUDModelSerializer,
    MilestoneListSerializer,
)
from apps.learning.config import BaseUploadStatusChoices
from apps.my_learning.models import Report
from apps.my_learning.serializers.v1 import ReportEmailCreateSerializer
from apps.my_learning.tasks import LeaderboardReportGenerationTask
from apps.tenant_service.middlewares import get_current_db_name


class MilestoneCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api Viewset to create, update & delete `Milestone`."""

    serializer_class = MilestoneCUDModelSerializer
    queryset = Milestone.objects.alive()


class MilestoneListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Milestone."""

    queryset = Milestone.objects.alive()
    serializer_class = MilestoneListSerializer
    search_fields = ["name"]


class LeaderboardActivityListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list `LeaderboardActivity`."""

    serializer_class = LeaderboardActivityListSerializer
    queryset = LeaderboardActivity.objects.all()
    search_fields = ["user__email", "user__first_name", "user__last_name", "user__id", "user__uuid"]
    filterset_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "user__id",
        "user__uuid",
        "course_id",
        "learning_path_id",
    ]


class LeaderboardListApiViewSet(AppModelListAPIViewSet):
    """Leaderboard List API Viewset."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Serializer class for the same view."""

        total_points = serializers.SerializerMethodField()
        is_competitor = serializers.SerializerMethodField()
        profile_picture = UserProfilePictureRetrieveSerializer()

        def get_total_points(self, user):
            """Return the total points which is already calculated in the view's queryset."""

            return getattr(user, "total_points", 0)

        def get_is_competitor(self, user):
            """Return whether the user is a competitor."""

            try:
                return user in self.get_user().related_leaderboard_competition.competitors.all()
            except Exception:
                return False

        class Meta:
            model = User
            fields = [
                "id",
                "uuid",
                "first_name",
                "last_name",
                "profile_picture",
                "total_points",
                "is_competitor",
            ]

    serializer_class = _Serializer
    queryset = User.objects.active()
    filterset_fields = [
        "email",
        "first_name",
        "last_name",
        "id",
        "uuid",
        "related_leaderboard_activities__course__name",
    ]
    search_fields = ["email", "first_name", "last_name", "id", "uuid"]

    def get_queryset(self):
        """Overridden to include course based filter"""

        queryset = super().get_queryset()
        if course_id := self.request.query_params.get("course_id"):
            queryset = queryset.filter(related_leaderboard_activities__course_id=course_id)
        if learning_path_id := self.request.query_params.get("learning_path_id"):
            queryset = queryset.filter(related_leaderboard_activities__learning_path_id=learning_path_id)
        queryset = queryset.annotate(total_points=Coalesce(Sum("related_leaderboard_activities__points"), 0)).order_by(
            "-total_points"
        )
        return queryset

    # def get_queryset(self):
    #     """Overridden to include course based filtering."""
    #
    #     time_param = self.request.query_params.get("time_param")
    #     queryset = super().get_queryset()
    #
    #     if time_param == "day":
    #         queryset = (
    #             queryset.annotate(day=TruncDate("related_leaderboard_activities__created_at"))
    #             .annotate(total_points=Sum("related_leaderboard_activities__points"))
    #             .order_by("total_points")
    #         )
    #     elif time_param == "month":
    #         queryset = (
    #             queryset.annotate(
    #                 month=TruncMonth("related_leaderboard_activities__created_at"),
    #             )
    #             .annotate(total_points=Sum("related_leaderboard_activities__points"))
    #             .order_by("total_points")
    #         )
    #     elif time_param == "year":
    #         queryset = (
    #             queryset.annotate(
    #                 year=TruncYear("related_leaderboard_activities__created_at"),
    #             )
    #             .annotate(total_points=Sum("related_leaderboard_activities__points"))
    #             .order_by("total_points")
    #         )
    #     else:
    #         queryset = queryset.annotate(total_points=Sum("related_leaderboard_activities__points")).order_by(
    #             "total_points"
    #         )
    #     return queryset

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Meta for filtering."""

        data = {"filter_fields": self.filterset_fields}
        return self.send_response(data)


class LeaderboardCompetitionApiView(AppAPIView):
    """Api viewset to Retrieve `LeaderboardCompetition`."""

    serializer_class = LeaderboardCompetitionDetailSerializer

    def get(self, request, *args, **kwargs):
        """Return a LeaderboardCompetition Detail object."""

        instance = LeaderboardCompetition.objects.get_or_create(user=self.request.user)[0]
        return self.send_response(self.serializer_class(instance).data)


class LeaderboardCompetitionUpdateApiView(AppAPIView):
    """Api viewset to Retrieve `LeaderboardCompetition`."""

    class LBUpdateSerializer(AppSerializer):
        """Serializer class for the same view."""

        competitor = serializers.PrimaryKeyRelatedField(queryset=User.objects.alive())
        as_competitor = serializers.BooleanField(default=False)

        def validate_competitor(self, competitor):
            """Check if the user is already a competitor or self."""

            instance: LeaderboardCompetition = LeaderboardCompetition.objects.get_or_create(user=self.get_user())[0]
            if self.get_user() == competitor:
                raise serializers.ValidationError("You cannot add yourself as a competitor.")
            self.context["instance"] = instance
            return competitor

        def validate(self, attrs):
            """Validate custom logic to add or remove competitor."""

            competitor = attrs["competitor"]
            instance = self.context["instance"]

            if attrs["as_competitor"]:
                if competitor in instance.competitors.all():
                    raise serializers.ValidationError({"competitor": "This user is already a competitor."})
            elif competitor not in instance.competitors.all():
                raise serializers.ValidationError({"competitor": "This user is not a competitor."})
            return attrs

    serializer_class = LBUpdateSerializer

    def post(self, request, *args, **kwargs):
        """Update LeaderboardCompetition for the current user."""

        serializer = self.get_valid_serializer()
        instance = serializer.context["instance"]
        if serializer.validated_data["as_competitor"]:
            instance.competitors.add(serializer.validated_data["competitor"])
        else:
            instance.competitors.remove(serializer.validated_data["competitor"])
        instance.save()
        return self.send_response(data={"message": "Competition updated successfully."})


class LeaderboardReportAPIView(AppAPIView):
    """APIView to generate Leaderboard Report"""

    class _Serializer(ReportEmailCreateSerializer):
        """Serializer to handle Leaderboard Report"""

        leaderboard_time_param = serializers.ChoiceField(
            choices=TimePeriodChoices.choices, allow_null=True, required=False
        )
        name = serializers.CharField(required=True)
        time_param = serializers.CharField(allow_null=True, required=False)

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Handle on Post"""

        validated_data = self.get_valid_serializer().validated_data
        validated_data["data"] = {
            "is_leaderboard_report": True,
            "leaderboard_time_param": validated_data.pop("leaderboard_time_param"),
            "time_param": validated_data.pop("time_param"),
            "recipients": [recipient.email for recipient in validated_data.pop("recipients", [])],
            "is_send_email": validated_data.pop("is_send_email", None),
        }
        report_instance = Report.objects.create(created_by=self.get_user(), **validated_data)
        report_instance.status = BaseUploadStatusChoices.initiated
        report_instance.save()
        LeaderboardReportGenerationTask().run_task(
            report_instance_id=report_instance.id, db_name=get_current_db_name()
        )
        return self.send_response()
