from django.urls import path

from apps.my_learning.views.api.v1 import LearningRecommendationAPIView

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning"

urlpatterns = [
    path(
        f"{API_URL_PREFIX}/recommendations/",
        LearningRecommendationAPIView.as_view(),
    ),
]
