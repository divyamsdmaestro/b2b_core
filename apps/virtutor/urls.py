from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.virtutor.views.api.v1 import (
    AssignedTrainerListApiView,
    AssignTrainerApiView,
    AssignTrainerMetaApiView,
    MODTrainerListApiView,
    RemoveTrainerApiView,
    ScheduledSessionManagementApiView,
    ScheduleSessionApiView,
    SessionPaticipantListApiView,
    SessionPaticipantUpdateApiView,
    SessionRecordingsURLApiView,
    SessionStartApiView,
    TrainerDetailApiView,
)

app_name = "virtutor"
API_URL_PREFIX = "api/v1/virtutor"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/trainer/list", AssignedTrainerListApiView)

urlpatterns = [
    path(f"{API_URL_PREFIX}/mod/trainer/list/", MODTrainerListApiView.as_view()),
    path(f"{API_URL_PREFIX}/assign/trainer/", AssignTrainerApiView.as_view()),
    path(f"{API_URL_PREFIX}/trainer/view-detail/<int:trainer_id>/", TrainerDetailApiView.as_view()),
    path(f"{API_URL_PREFIX}/assign/trainer/meta/", AssignTrainerMetaApiView.as_view()),
    path(f"{API_URL_PREFIX}/remove/trainer/", RemoveTrainerApiView.as_view()),
    path(f"{API_URL_PREFIX}/schedule/session/", ScheduleSessionApiView.as_view()),
    path(f"{API_URL_PREFIX}/start/session/<int:pk>/", SessionStartApiView.as_view()),
    path(f"{API_URL_PREFIX}/session/<int:pk>/recordings/", SessionRecordingsURLApiView.as_view()),
    path(
        f"{API_URL_PREFIX}/scheduled/session/management/",
        ScheduledSessionManagementApiView.as_view(),
    ),
    path(f"{API_URL_PREFIX}/session/<int:session_id>/participant/list/", SessionPaticipantListApiView.as_view()),
    path(f"{API_URL_PREFIX}/session/<int:session_id>/participant/update/", SessionPaticipantUpdateApiView.as_view()),
] + router.urls
