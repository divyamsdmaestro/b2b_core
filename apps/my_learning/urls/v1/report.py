from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1.report import ReportCreateAPIViewSet, ReportFileAPIView, ReportListAPIViewSet

app_name = "report"
API_URL_PREFIX = "api/v1/report"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", ReportListAPIViewSet)
router.register(f"{API_URL_PREFIX}/cd", ReportCreateAPIViewSet)

urlpatterns = [path(f"{API_URL_PREFIX}/<report_id>/file/", ReportFileAPIView.as_view())] + router.urls
