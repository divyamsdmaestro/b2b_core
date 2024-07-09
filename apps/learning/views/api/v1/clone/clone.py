from rest_framework import serializers

from apps.access_control.fixtures import PolicyChoices
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppSerializer
from apps.common.views.api import AppAPIView
from apps.learning.tasks import LearningCloneTask
from apps.my_learning.config import AssignmentLearningTypeChoices
from apps.tenant_service.middlewares import get_current_db_name


class LearningCloneApiView(AppAPIView):
    """Api view to clone the given ccms course."""

    class _Serializer(AppSerializer):
        """Serializer class for the same."""

        learning_type = serializers.ChoiceField(choices=AssignmentLearningTypeChoices.choices)
        learning_id = serializers.ListField(child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH))
        is_ccms_obj = serializers.BooleanField()

    serializer_class = _Serializer
    policy_slug = PolicyChoices.course_management

    def post(self, request, *args, **kwargs):
        """Clone the course logic."""

        validated_data = self.get_valid_serializer().validated_data
        clone_kwargs = {
            "learning_type": validated_data["learning_type"],
            "learning_id": validated_data["learning_id"],
            "is_ccms_obj": validated_data["is_ccms_obj"],
            "request_headers": {"headers": dict(self.get_request().headers)},
        }
        LearningCloneTask().run_task(db_name=get_current_db_name(), **clone_kwargs)
        return self.send_response(data="Cloning is in progress...")
