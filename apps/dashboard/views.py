from apps.common.views.api import AppAPIView
from apps.dashboard.models import PowerBIDetail


class DashboardApiView(AppAPIView):
    """Api viewset to get role based user dashboard."""

    def get(self, request, *args, **kwargs):
        """Logic for the same."""

        if not request.user.current_role:
            return self.send_error_response(data={"message": "User role is not specified. Please contact support."})
        try:
            data = PowerBIDetail.get_dashboard_data(request.user)
        except ValueError as error:
            return self.send_error_response(data={"message": f"{error}"})
        return self.send_response(data=data)


class ReportBuilderApiView(AppAPIView):
    """Api viewset to get role based report builder."""

    def get(self, request, *args, **kwargs):
        """Logic for the same."""

        if not request.user.current_role:
            return self.send_error_response(data={"message": "User role is not specified. Please contact support."})
        try:
            data = PowerBIDetail.get_report_builder_data(request.user)
        except ValueError as error:
            return self.send_error_response(data={"message": f"{error}"})
        return self.send_response(data=data)
