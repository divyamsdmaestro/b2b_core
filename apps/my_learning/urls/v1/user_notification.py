from django.urls import path

from apps.my_learning.views.api.v1 import UserNotificationAPIView

app_name = "user_notification"
API_URL_PREFIX = "api/v1"

urlpatterns = [
    path(f"{API_URL_PREFIX}/user/notification/", UserNotificationAPIView.as_view()),
]
