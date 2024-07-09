from apps.common.views.api.base import AppAPIView
from apps.learning.serializers.v1 import LearningRetireSerializer


class LearningRetireApiView(AppAPIView):
    """Api view to add retirement date to learning instance."""

    serializer_class = LearningRetireSerializer

    def post(self, request, *args, **kwargs):
        """Handle on post."""

        validated_data = self.get_valid_serializer().validated_data
        instance = validated_data["instance"]
        instance.retirement_date = validated_data["retirement_date"]
        if not validated_data.get("is_retired"):
            instance.is_retired = False
            instance.is_active = True
        instance.save()
        return self.send_response("Retirement Scheduled Successfully.")
