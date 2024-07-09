from django.core.files.storage import default_storage
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.learning.config import BaseUploadStatusChoices
from apps.my_learning.models import Report
from apps.my_learning.serializers.v1 import ReportCreateSerializer, ReportListSerializer


class ReportCreateAPIViewSet(AppModelCUDAPIViewSet):
    """Api View to generate a report"""

    serializer_class = ReportCreateSerializer
    queryset = Report.objects.all()


class ReportListAPIViewSet(AppModelListAPIViewSet):
    """Api Viewset to list the reports"""

    queryset = Report.objects.all().order_by("-created_at")
    serializer_class = ReportListSerializer
    search_fields = ["name", "status"]

    def get_queryset(self):
        """Overriden to filter the queryset based on the master/advanced/file-submission report."""

        queryset = super().get_queryset()
        if bool(self.request.query_params.get("is_master_report")):
            queryset = queryset.filter(data__is_master_report=True)
        elif bool(self.request.query_params.get("is_file_submission")):
            queryset = queryset.filter(data__is_file_submission=True)
        elif bool(self.request.query_params.get("is_leaderboard_report")):
            queryset = queryset.filter(data__is_leaderboard_report=True)
        elif bool(self.request.query_params.get("is_feedback_report")):
            queryset = queryset.filter(data__is_feedback_report=True)
        else:
            queryset = queryset.filter(
                data__is_master_report=False, data__is_file_submission=False, data__is_feedback_report=False
            )
        return queryset


class ReportFileAPIView(AppAPIView):
    """API View to get the report file."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        report = get_object_or_404(Report, id=kwargs.get("report_id"))
        if report.status != BaseUploadStatusChoices.completed:
            return self.send_error_response(data={"status": f"Report Generation Status: {report.status}"})
        file_url = report.file_url
        file_path = file_url.split("media/")[-1]
        exact_path = file_path.replace("%20", " ")
        if not default_storage.exists(exact_path):
            return self.send_error_response("File not found.")
        with default_storage.open(exact_path, "rb") as file:
            file_content = file.read()
        response = Response(
            headers={"Content-Disposition": "attachment; filename=report_file.xlsx"},
            content_type="application/ms-excel",
        )
        response.content = file_content
        return response
