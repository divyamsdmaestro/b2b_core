from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, get_upload_api_view
from apps.meta.models import Faculty, FacultyImageModel
from apps.meta.serializers.v1 import FacultyCUDModelSerializer, FacultyListModelSerializer

FacultyImageUploadAPIView = get_upload_api_view(meta_model=FacultyImageModel, meta_fields=["id", "image"])


class FacultyCUDModelApiViewSet(AppModelCUDAPIViewSet):
    """Api view for Faculty model"""

    serializer_class = FacultyCUDModelSerializer
    queryset = Faculty.objects.all()


class FacultyListModelApiViewSet(AppModelListAPIViewSet):
    """Api view to list the faculty details."""

    serializer_class = FacultyListModelSerializer
    queryset = Faculty.objects.all()
    search_fields = ["name", "type"]

    def get_queryset(self):
        """Overriden to filter the queryset based on course, lp & alp."""

        queryset = super().get_queryset()
        if course_id := self.request.query_params.get("course"):
            queryset = queryset.filter(related_courses__id=course_id).distinct()
        elif lp_id := self.request.query_params.get("learning_path"):
            queryset = queryset.filter(
                related_courses__related_learning_path_courses__learning_path_id=lp_id
            ).distinct()
        elif alp_id := self.request.query_params.get("advanced_learning_path"):
            queryset = queryset.filter(
                related_courses__related_learning_path_courses__learning_path__related_alp_learning_paths__advanced_learning_path_id=alp_id  # noqa
            ).distinct()
        elif st_id := self.request.query_params.get("skill_traveller"):
            queryset = queryset.filter(
                related_courses__related_skill_traveller_courses__skill_traveller_id=st_id
            ).distinct()
        return queryset
