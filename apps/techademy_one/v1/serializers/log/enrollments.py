from apps.access_control.serializers.v1 import UserGroupReadOnlySerializer
from apps.common.idp_service import idp_admin_auth_token
from apps.common.serializers import AppReadOnlyModelSerializer, BaseIDNameSerializer
from apps.my_learning.models import Enrollment
from apps.my_learning.serializers.v1.tracker.common import Basic_enrollment_fields


class T1EnrollmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for list model serializer."""

    course = BaseIDNameSerializer(read_only=True)
    learning_path = BaseIDNameSerializer(read_only=True)
    advanced_learning_path = BaseIDNameSerializer(read_only=True)
    skill_traveller = BaseIDNameSerializer(read_only=True)
    playground = BaseIDNameSerializer(read_only=True)
    playground_group = BaseIDNameSerializer(read_only=True)
    assignment_group = BaseIDNameSerializer(read_only=True)
    user = BaseIDNameSerializer(read_only=True)
    user_group = UserGroupReadOnlySerializer(read_only=True)
    created_by = BaseIDNameSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Enrollment
        fields = Basic_enrollment_fields + [
            "id",
            "uuid",
            "user",
            "user_group",
            "created_by",
            "action",
            "reason",
            "approval_type",
            "actionee",
            "is_enrolled",
            "learning_status",
            "created_at",
            "start_date",
            "end_date",
            "action_date",
        ]

    def to_representation(self, instance):
        """Overridden to return the ccms detail if it was a ccms obj."""

        from apps.learning.helpers import get_ccms_retrieve_details

        results = super().to_representation(instance)
        auth_token = idp_admin_auth_token(raise_drf_error=False)
        request_headers_data = {"headers": {"Idp-Token": auth_token}}
        if instance.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type=instance.learning_type, instance_id=str(instance.ccms_id), request=request_headers_data
            )
            if success:
                results["ccms_id"] = data["data"]
                return results
            results["ccms_id"] = None
        return results
