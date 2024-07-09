from django.urls import path

from apps.learning.views.api.v1 import LearningRetireApiView

app_name = "learning_retire"
API_URL_PREFIX = "api/v1/learning/retire"

urlpatterns = [
    path(f"{API_URL_PREFIX}/update/", LearningRetireApiView.as_view(), name="learning-retire-update"),
]
