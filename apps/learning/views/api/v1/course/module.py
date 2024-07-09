from rest_framework import serializers

from apps.access_control.fixtures import PolicyChoices
from apps.common.pagination import TempPagination
from apps.common.serializers import AppSerializer
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import CourseModule
from apps.learning.serializers.v1 import (
    CourseModuleCUDModelSerializer,
    CourseModuleListModelSerializer,
    CourseModuleRetrieveSerializer,
)


class CourseModuleCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete modules."""

    queryset = CourseModule.objects.alive()
    serializer_class = CourseModuleCUDModelSerializer
    policy_slug = PolicyChoices.course_management


class CourseModuleListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list course modules."""

    serializer_class = CourseModuleListModelSerializer
    queryset = CourseModule.objects.alive()
    pagination_class = TempPagination
    policy_slug = PolicyChoices.course_management

    def get_queryset(self):
        """Overridden the queryset to filter the modules based on courses"""

        course_id = self.kwargs.get("course_pk")
        return CourseModule.objects.alive().filter(course=course_id).order_by("sequence", "created_at")


class CourseModuleRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Retrieve api view for course module."""

    serializer_class = CourseModuleRetrieveSerializer
    queryset = CourseModule.objects.alive()
    policy_slug = PolicyChoices.course_management


class CourseModuleSequenceUpdateAPIView(AppAPIView):
    """API View to update Sequence of Course Module"""

    class CourseModuleSequenceSerializer(AppSerializer):
        """Serializer class for Module Sequence"""

        module = serializers.PrimaryKeyRelatedField(queryset=CourseModule.objects.alive(), required=True)
        sequence = serializers.IntegerField(required=True)

        def validate(self, attrs):
            """function to validate the sequence"""

            last_module = CourseModule.objects.filter(course=attrs["module"].course).order_by("sequence").last()
            if attrs["sequence"] > last_module.sequence:
                raise serializers.ValidationError({"sequence": "Invalid sequence"})
            return attrs

    serializer_class = CourseModuleSequenceSerializer

    def post(self, request, *args, **kwargs):
        """Handle on Post"""

        validated_data = self.get_valid_serializer().validated_data
        module, sequence = validated_data["module"], validated_data["sequence"]
        module.course.update_module_sequence(to_sequence=sequence, module=module)
        return self.send_response(data="Success")
