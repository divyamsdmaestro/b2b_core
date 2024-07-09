from django.urls import path

from apps.my_learning.views.api.v1.one_profile import (
    OneProfileAssessmentInfoAPIView,
    OneProfileCourseInfoAPIView,
    OneProfileUserInfoAPIView,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning"

urlpatterns = [
    path(
        f"{API_URL_PREFIX}/one-profile/user/info/",
        OneProfileUserInfoAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}/one-profile/assessment/info/",
        OneProfileAssessmentInfoAPIView.as_view(),
    ),
    path(
        f"{API_URL_PREFIX}/one-profile/course/info/",
        OneProfileCourseInfoAPIView.as_view(),
    ),
]
