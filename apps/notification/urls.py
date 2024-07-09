from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.notification.views import NotificationListApiViewSet, NotificationUpdateApiView

app_name = "notification"
API_URL_PREFIX = "api/v1/notifications"

router = AppSimpleRouter()
router.register(f"{API_URL_PREFIX}/list", NotificationListApiViewSet)


urlpatterns = [
    path(
        f"{API_URL_PREFIX}/bulk-update/",
        NotificationUpdateApiView.as_view(),
        name="notifications-update",
    ),
] + router.urls
