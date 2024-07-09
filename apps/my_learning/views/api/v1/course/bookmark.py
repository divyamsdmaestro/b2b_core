from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.learning.models import CourseSubModule
from apps.my_learning.models import UserCourseBookMark
from apps.my_learning.serializers.v1 import UserCourseBookMarkCUDSerializer, UserCourseBookMarkListSerializer


class UserCourseBookMarkCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to bookmark the course sub_modules."""

    serializer_class = UserCourseBookMarkCUDSerializer
    queryset = UserCourseBookMark.objects.all()


class UserCourseBookMarkListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the bookmarks based on sub_modules."""

    serializer_class = UserCourseBookMarkListSerializer
    queryset = UserCourseBookMark.objects.all()

    def get_queryset(self):
        """Overridden to return the bookmarks based on sub_modules."""

        sub_module_id = self.kwargs.get("sub_module_pk", None)
        sub_module_instance = get_object_or_404(CourseSubModule, id=sub_module_id)
        return UserCourseBookMark.objects.filter(
            sub_module_tracker__sub_module=sub_module_instance, user=self.get_user()
        )
