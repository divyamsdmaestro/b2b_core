from django.urls import path

from apps.common.routers import AppSimpleRouter

from .views.api.v1 import (
    BadgeActivityListApiViewSet,
    BadgeCUDApiViewSet,
    BadgeListApiViewSet,
    LeaderboardActivityListApiViewSet,
    LeaderboardCompetitionApiView,
    LeaderboardCompetitionUpdateApiView,
    LeaderboardListApiViewSet,
    LeaderboardReportAPIView,
    MilestoneCUDApiViewSet,
    MilestoneListApiViewSet,
    UserBadgeListApiViewSet,
)

app_name = "leaderboard"
API_URL_PREFIX = "api/v1/leaderboard"

router = AppSimpleRouter()
router.register(f"{API_URL_PREFIX}/list", LeaderboardListApiViewSet)
router.register(f"{API_URL_PREFIX}/activity/list", LeaderboardActivityListApiViewSet)
router.register(f"{API_URL_PREFIX}/milestone/list", MilestoneListApiViewSet)
router.register(f"{API_URL_PREFIX}/milestone/cud", MilestoneCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/badge/list", BadgeListApiViewSet)
router.register(f"{API_URL_PREFIX}/badge/cud", BadgeCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/badge/activity/list", BadgeActivityListApiViewSet)
router.register(f"{API_URL_PREFIX}/users/badge/list", UserBadgeListApiViewSet)


urlpatterns = [
    path(f"{API_URL_PREFIX}/my-competition/", LeaderboardCompetitionApiView.as_view(), name="my-competition"),
    path(
        f"{API_URL_PREFIX}/my-competition/update/",
        LeaderboardCompetitionUpdateApiView.as_view(),
        name="my-competition-update",
    ),
    path(f"{API_URL_PREFIX}/report/", LeaderboardReportAPIView.as_view(), name="leaderboard-report"),
] + router.urls
