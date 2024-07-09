from apps.common.views.api import AppAPIView, NonAuthenticatedAPIMixin
from apps.techademy_one.v1.serializers import T1BulkUserOnboardSerializer
from apps.techademy_one.v1.tasks import T1BulkUserOnboardTask


class T1BulkUserOnboardAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to Bulk create User."""

    serializer_class = T1BulkUserOnboardSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        # TODO: Authentication, super admin details integration.
        validated_data = self.get_valid_serializer().validated_data
        tenant_obj = validated_data.pop("tenant_obj", None)
        user_details = validated_data["user_details"]
        if not user_details:
            return self.send_error_response(data="No data supplied.")
        T1BulkUserOnboardTask().run_task(tenant_id=tenant_obj.id, user_details=user_details)
        return self.send_response(data={"message": "Users will be onboarded shortly."})
