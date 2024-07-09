from django.urls import path

from apps.common.routers import AppSimpleRouter

from .views.api.v1 import CalendarActivityCUDApiViewSet, CalendarActivityDeleteApiView, CalendarActivityListApiView

app_name = "event"
API_URL_PREFIX = "api/v1/calendar"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/activity/cud", CalendarActivityCUDApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/activity/delete/", CalendarActivityDeleteApiView.as_view()),
    path(f"{API_URL_PREFIX}/activity/list/", CalendarActivityListApiView.as_view()),
] + router.urls
