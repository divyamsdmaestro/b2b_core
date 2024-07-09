from django.db.models import Q

from apps.common.views.api import AppAPIView
from apps.learning.config import BaseUploadStatusChoices
from apps.learning.models.course.course import Course
from apps.my_learning.models import Report
from apps.my_learning.tasks import ReportGenerationTask
from apps.tenant_extension.v1.serializers import CustomReportSerializer, CustomReportStatusSerializer
from apps.tenant_service.middlewares import get_current_db_name


class CustomReportAPIView(AppAPIView):
    """Api view to generate Master report for Tenant. Specifically for Prolifics."""

    serializer_class = CustomReportSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        validated_data = self.get_valid_serializer().validated_data
        report_name = validated_data["report_name"]
        report = Report.objects.filter(name=report_name).first()
        report_data = Report.basic_data()
        report_type = validated_data["report_type"]
        report_data["report_type"] = report_type
        if report_type == "compliance":
            courses = Course.objects.filter(
                code__in=[
                    "Prolifics001",
                    "Prolifics002",
                    "Prolifics003",
                    "Prolifics004",
                    "Prolifics006",
                ]
            ).values_list("id", flat=True)
            report_data["course"] = list(courses)
            report_data["is_entire_learnings"] = False
        elif report_type == "cdp":
            # TODO: No context for CDP yet so not handling the filtering of courses.
            report_data["is_entire_learnings"] = False
        if not report:
            report = Report.objects.create(
                name=report_name,
                status=BaseUploadStatusChoices.initiated,
                start_date=validated_data["start_date"],
                end_date=validated_data["end_date"],
                data=report_data,
            )
            ReportGenerationTask().run_task(
                report_instance_id=report.id,
                db_name=get_current_db_name(),
                request_headers={"headers": dict(request.headers)},
            )
        return self.send_response(
            data={
                "report_id": report.uuid,
                "report_name": report_name,
                "file_url": report.file_url,
                "status": report.status,
            }
        )


class CustomReportStatusAPIView(AppAPIView):
    """Api view to check Tenant Master Report status. Specifically for Prolifics."""

    serializer_class = CustomReportStatusSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        validated_data = self.get_valid_serializer().validated_data
        report = Report.objects.filter(
            Q(name=validated_data.get("report_name")) | Q(uuid=validated_data.get("report_id"))
        ).first()
        if not report:
            self.send_error_response(data={"message": "Invalid Report Name Or ID."})
        return self.send_response(
            data={
                "report_id": report.uuid,
                "report_name": report.name,
                "file_url": report.file_url,
                "status": report.status,
            }
        )
