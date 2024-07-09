from django.db.models import Q
from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppAPIView, NonAuthenticatedAPIMixin
from apps.learning.config import BaseUploadStatusChoices
from apps.my_learning.models import Report
from apps.my_learning.tasks import ReportGenerationTask
from apps.techademy_one.v1.serializers import T1TenantMasterReportSerializer, T1TenantMasterReportStatusSerializer
from apps.tenant.models import Tenant
from apps.tenant_service.middlewares import get_current_db_name, set_db_for_router


class T1TenantMasterReportAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to generate Master report for Tenant."""

    serializer_class = T1TenantMasterReportSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        validated_data = self.get_valid_serializer().validated_data
        tenant_id, report_name = validated_data["tenant_id"], validated_data["report_name"]
        start_date, end_date = validated_data.get("start_date", None), validated_data.get("end_date", None)
        is_date_skipped = False
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Invalid Tenant ID."})

        tenant.db_router.add_db_connection()
        set_db_for_router(tenant.db_name)
        report = Report.objects.filter(name=report_name).first()
        if not start_date or not end_date:
            is_date_skipped = True
        if not report:
            report = Report.objects.create(
                name=report_name,
                status=BaseUploadStatusChoices.initiated,
                start_date=validated_data.get("start_date", None),
                end_date=validated_data.get("end_date", None),
                data=Report.basic_data(is_date_skipped=is_date_skipped),
            )
            ReportGenerationTask().run_task(
                report_instance_id=report.id,
                db_name=get_current_db_name(),
                request_headers={"headers": dict(request.headers)},
            )

        # TODO: Authentication, super admin details integration.
        return self.send_response(
            data={
                "tenant_id": tenant_id,
                "report_id": report.uuid,
                "report_name": report_name,
                "file_url": report.file_url,
                "status": report.status,
            }
        )


class T1TenantMasterReportStatusAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to check Tenant Master Report status."""

    serializer_class = T1TenantMasterReportStatusSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        # TODO: Authentication, super admin details integration.
        validated_data = self.get_valid_serializer().validated_data
        tenant = get_object_or_404(Tenant, uuid=validated_data["tenant_id"])
        tenant.db_router.add_db_connection()
        set_db_for_router(tenant.db_name)
        report = Report.objects.filter(
            Q(name=validated_data.get("report_name")) | Q(uuid=validated_data.get("report_id"))
        ).first()
        if not report:
            self.send_error_response(data={"message": "Invalid Report Name Or ID."})
        return self.send_response(
            data={
                "tenant_id": tenant.uuid,
                "report_id": report.uuid,
                "report_name": report.name,
                "file_url": report.file_url,
                "status": report.status,
            }
        )
