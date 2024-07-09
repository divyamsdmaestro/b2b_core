from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import ScormListApiViewSet, ScormUDApiViewSet, ScormUploadApiView

app_name = "scorm"
API_URL_PREFIX = "api/v1/scorm"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/ud", ScormUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", ScormListApiViewSet)

urlpatterns = [path(f"{API_URL_PREFIX}/upload/", ScormUploadApiView.as_view())] + router.urls
