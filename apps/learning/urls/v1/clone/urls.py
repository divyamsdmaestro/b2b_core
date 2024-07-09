from django.urls import path

from apps.learning.views.api.v1 import LearningCloneApiView

app_name = "learning_clone"
API_URL_PREFIX = "api/v1/learning"

urlpatterns = [
    # Clone Learning API
    path(f"{API_URL_PREFIX}/clone/", LearningCloneApiView.as_view(), name="learning-clone"),
]
