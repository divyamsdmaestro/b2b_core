from django.urls import path

from apps.my_learning.views.api.v1 import UserFeedPageApiView

app_name = "user_feed"
API_URL_PREFIX = "api/v1"

urlpatterns = [
    path(f"{API_URL_PREFIX}/user/feed/page/", UserFeedPageApiView.as_view()),
]
