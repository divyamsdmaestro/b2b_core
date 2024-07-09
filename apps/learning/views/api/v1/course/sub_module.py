from apps.access_control.fixtures import PolicyChoices
from apps.common.pagination import TempPagination
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.learning.models import CourseSubModule
from apps.learning.serializers.v1 import CourseSubModuleCUDSerializer, CourseSubModuleListSerializer


class CourseSubModuleCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete sub modules."""

    serializer_class = CourseSubModuleCUDSerializer
    queryset = CourseSubModule.objects.alive()
    policy_slug = PolicyChoices.course_management

    def get_serializer_context(self):
        """Include the learning type."""

        context = super().get_serializer_context()
        context["learning_type"] = "sub_module"
        return context


class CourseSubModuleListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to retrieve sub_modules."""

    serializer_class = CourseSubModuleListSerializer
    queryset = CourseSubModule.objects.alive()
    pagination_class = TempPagination
    policy_slug = PolicyChoices.course_management

    def get_queryset(self):
        """Overridden the queryset to filter the sub_modules based on modules"""

        module_id = self.request.query_params.get("module")
        return CourseSubModule.objects.alive().filter(module=module_id).order_by("sequence", "created_at")
