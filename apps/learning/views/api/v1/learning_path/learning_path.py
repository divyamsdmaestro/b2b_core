from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from apps.access_control.fixtures import PolicyChoices
from apps.common.serializers import AppSerializer
from apps.common.views.api import (
    AppAPIView,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    get_upload_api_view,
)
from apps.learning.models import LearningPath, LearningPathCourse, LearningPathImageModel, LearningPathResource
from apps.learning.serializers.v1 import (
    LearningPathCUDModelSerializer,
    LearningPathListModelSerializer,
    LearningPathResourceCreateModelSerializer,
    LearningPathResourceListModelSerializer,
    LearningPathRetrieveModelSerializer,
    LPCourseAllocationCUDSerializer,
    LPCourseListModelSerializer,
)
from apps.learning.views.api.v1 import BaseLearningSkillRoleListApiViewSet

LearningPathImageUploadAPIView = get_upload_api_view(meta_model=LearningPathImageModel, meta_fields=["id", "image"])


class LearningPathCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete learning_paths."""

    serializer_class = LearningPathCUDModelSerializer
    queryset = LearningPath.objects.alive()
    policy_slug = PolicyChoices.learning_path_management


class LearningPathListApiViewSet(BaseLearningSkillRoleListApiViewSet):
    """View to list learning_paths."""

    queryset = LearningPath.objects.alive().order_by("created_at")
    serializer_class = LearningPathListModelSerializer
    filterset_fields = BaseLearningSkillRoleListApiViewSet.filterset_fields + ["learning_type"]
    policy_slug = PolicyChoices.learning_path_management
    user_group_filter_key = "related_learning_catalogues__related_catalogue_relations__user_group__id__in"


class LearningPathRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve the learning_path."""

    serializer_class = LearningPathRetrieveModelSerializer
    queryset = LearningPath.objects.alive()
    policy_slug = PolicyChoices.learning_path_management


class LPCourseAllocationCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to CUD for LP courses."""

    serializer_class = LPCourseAllocationCUDSerializer
    queryset = LearningPathCourse.objects.all()
    policy_slug = PolicyChoices.learning_path_management


class LPCourseListApiViewSet(AppModelListAPIViewSet):
    """View to retrieve the courses in learning path."""

    serializer_class = LPCourseListModelSerializer
    queryset = LearningPathCourse.objects.all().order_by("sequence")
    filterset_fields = ["learning_path", "sequence"]
    policy_slug = PolicyChoices.learning_path_management

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        learning_path = self.serializer_class().serialize_for_meta(LearningPath.objects.alive(), fields=["id", "name"])
        data = {"learning_path": learning_path}
        return self.send_response(data)


class LearningPathCloneApiView(AppAPIView):
    """Api view to clone the given LearningPath."""

    class _Serializer(AppSerializer):
        """Serializer class for the same."""

        learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.alive())

    serializer_class = _Serializer
    policy_slug = PolicyChoices.learning_path_management

    def post(self, request, *args, **kwargs):
        """Clone the LearningPath logic."""

        serializer = self.get_valid_serializer()
        learning_path: LearningPath = serializer.validated_data["learning_path"]
        clone_details = learning_path.clone()
        return self.send_response(data=clone_details)


class LearningPathResourceApiViewSet(AppModelCUDAPIViewSet):
    """Api view to upload the resources for LearningPath."""

    serializer_class = LearningPathResourceCreateModelSerializer
    queryset = LearningPathResource.objects.all()
    policy_slug = PolicyChoices.learning_path_management

    def get_serializer_context(self):
        """Include the learning type."""

        context = super().get_serializer_context()
        context["learning_type"] = "learning_path"
        return context


class LearningPathResourceListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the LearningPath resources."""

    serializer_class = LearningPathResourceListModelSerializer
    queryset = LearningPathResource.objects.all()
    policy_slug = PolicyChoices.learning_path_management

    def get_queryset(self):
        """Overridden to provide the list of LearningPath resources."""

        learning_path_pk = self.kwargs.get("learning_path_pk", None)
        learning_path_instance = get_object_or_404(LearningPath, pk=learning_path_pk)

        return learning_path_instance.related_learning_path_resources.all()
