from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import YakshaAssessmentTrackerListApiView, YakshaAttemptUpdateApiView

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/yaksha/assessment"

router = AppSimpleRouter()


urlpatterns = [
    path(f"{API_URL_PREFIX}/tracker/list/", YakshaAssessmentTrackerListApiView.as_view()),
    path(f"{API_URL_PREFIX}/attempt/update/", YakshaAttemptUpdateApiView.as_view()),
] + router.urls
