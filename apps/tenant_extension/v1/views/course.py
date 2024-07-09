from apps.common.pagination import TempPagination
from apps.common.permissions import ExtTenantAPIAccessPermission
from apps.common.views.api import AppModelListAPIViewSet, NonAuthenticatedAPIMixin
from apps.learning.models import Course
from apps.learning.models.course.module import CourseModule
from apps.learning.serializers.v1.course.course import CourseListModelSerializer
from apps.learning.serializers.v1.course.module import CourseModuleListModelSerializer


class ExtCourseListApiViewSet(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """Api viewset to list courses."""

    queryset = Course.objects.alive().order_by("created_at")
    serializer_class = CourseListModelSerializer
    permission_classes = [ExtTenantAPIAccessPermission]


class ExtCourseModuleListApiViewSet(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """Api viewset to list course modules."""

    serializer_class = CourseModuleListModelSerializer
    queryset = CourseModule.objects.alive()
    pagination_class = TempPagination
    permission_classes = [ExtTenantAPIAccessPermission]

    def get_queryset(self):
        """Overridden the queryset to filter the modules based on courses"""

        course_id = self.kwargs.get("course_pk")
        return CourseModule.objects.alive().filter(course=course_id).order_by("sequence", "created_at")
