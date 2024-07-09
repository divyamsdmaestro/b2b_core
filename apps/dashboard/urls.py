from django.urls import path

from apps.dashboard.views import DashboardApiView, ReportBuilderApiView

app_name = "dashboard"
API_URL_PREFIX = "api/v1/dashboard"

urlpatterns = [
    path(f"{API_URL_PREFIX}/view/", DashboardApiView.as_view(), name="dashboard-view"),
    path(f"{API_URL_PREFIX}/report-builder/view/", ReportBuilderApiView.as_view(), name="report-builder-view"),
]
