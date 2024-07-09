from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.learning.models import CourseSubModule
from apps.my_learning.models import UserCourseNotes
from apps.my_learning.serializers.v1 import UserCourseNotesCUDSerializer, UserCourseNotesListModelSerializer


class UserCourseNotesCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to create, update & delete notes."""

    serializer_class = UserCourseNotesCUDSerializer
    queryset = UserCourseNotes.objects.all()


class UserCourseNotesListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the notes."""

    serializer_class = UserCourseNotesListModelSerializer
    queryset = UserCourseNotes.objects.all()
    filterset_fields = ["sub_module"]

    def get_serializer_context(self):
        """Include the submodule instance."""

        context = super().get_serializer_context()
        sub_module_id = self.kwargs.get("sub_module_pk", None)
        context["sub_module_instance"] = get_object_or_404(CourseSubModule, id=sub_module_id)
        return context

    def get_queryset(self):
        """Overridden to return the notes based on submodules."""

        sub_module_instance = self.get_serializer_context()["sub_module_instance"]
        return sub_module_instance.related_user_course_notes.filter(user=self.get_user())

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        context = self.get_serializer_context()
        sub_module_instance = context["sub_module_instance"]
        sub_module = self.serializer_class().serialize_for_meta(
            CourseSubModule.objects.filter(module__course=sub_module_instance.module.course), fields=["id", "name"]
        )
        return self.send_response({"sub_module": sub_module})
