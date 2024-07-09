from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    ExpertApproveApiView,
    ExpertCUDApiViewSet,
    ExpertListApiViewSet,
    ExpertRetrieveApiViewSet,
)

app_name = "expert"
API_URL_PREFIX = "api/v1/expert"
router = AppSimpleRouter()

# Expert Api's
router.register(f"{API_URL_PREFIX}/cud", ExpertCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", ExpertListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", ExpertRetrieveApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/approve/", ExpertApproveApiView.as_view(), name="expert-approve"),
] + router.urls
