from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from apps.access_control.fixtures import PolicyChoices
from apps.common.views.api import (
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    get_upload_api_view,
)
from apps.learning.models import (
    AdvancedLearningPath,
    AdvancedLearningPathImageModel,
    AdvancedLearningPathResource,
    ALPLearningPath,
)
from apps.learning.serializers.v1 import (
    AdvancedLearningPathCUDModelSerializer,
    AdvancedLearningPathListModelSerializer,
    AdvancedLearningPathRetrieveModelSerializer,
    ALPLearningPathCUDModelSerializer,
    ALPLearningPathListModelSerializer,
    AlpResourceCreateModelSerializer,
    AlpResourceListModelSerializer,
)
from apps.learning.views.api.v1 import BaseLearningSkillRoleListApiViewSet

AdvancedLearningPathImageUploadAPIView = get_upload_api_view(
    meta_model=AdvancedLearningPathImageModel, meta_fields=["id", "image"]
)


class AdvancedLearningPathCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete advanced_learning_paths."""

    serializer_class = AdvancedLearningPathCUDModelSerializer
    queryset = AdvancedLearningPath.objects.alive()
    policy_slug = PolicyChoices.advanced_learning_path_management


class AdvancedLearningPathListApiViewSet(BaseLearningSkillRoleListApiViewSet):
    """View to list advanced_learning_paths."""

    serializer_class = AdvancedLearningPathListModelSerializer
    queryset = AdvancedLearningPath.objects.alive().order_by("created_at")
    policy_slug = PolicyChoices.advanced_learning_path_management
    user_group_filter_key = "related_learning_catalogues__related_catalogue_relations__user_group__id__in"


class AdvancedLearningPathRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve advanced_learning_path."""

    serializer_class = AdvancedLearningPathRetrieveModelSerializer
    queryset = AdvancedLearningPath.objects.alive()
    policy_slug = PolicyChoices.advanced_learning_path_management


class ALPLearningPathCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view for ALP learning path CUD."""

    serializer_class = ALPLearningPathCUDModelSerializer
    queryset = ALPLearningPath.objects.all()
    policy_slug = PolicyChoices.advanced_learning_path_management


class ALPLearningPathListApiViewSet(AppModelListAPIViewSet):
    """View to retrieve the learning_paths in advanced learning path."""

    serializer_class = ALPLearningPathListModelSerializer
    queryset = ALPLearningPath.objects.all().order_by("sequence")
    filterset_fields = ["advanced_learning_path", "sequence"]
    policy_slug = PolicyChoices.advanced_learning_path_management

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        advanced_learning_path = self.serializer_class().serialize_for_meta(
            AdvancedLearningPath.objects.alive(), fields=["id", "name"]
        )

        data = {
            "advanced_learning_path": advanced_learning_path,
        }
        return self.send_response(data)


class AdvancedLearningPathResourceApiViewSet(AppModelCUDAPIViewSet):
    """Api view to upload the resources for Alp."""

    serializer_class = AlpResourceCreateModelSerializer
    queryset = AdvancedLearningPathResource.objects.all()
    policy_slug = PolicyChoices.advanced_learning_path_management

    def get_serializer_context(self):
        """Include the learning type."""

        context = super().get_serializer_context()
        context["learning_type"] = "advanced_learning_path"
        return context


class AdvancedLearningPathResourceListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the Alp resources."""

    serializer_class = AlpResourceListModelSerializer
    queryset = AdvancedLearningPathResource.objects.all()
    policy_slug = PolicyChoices.advanced_learning_path_management

    def get_queryset(self):
        """Overridden to provide the list of Alp resources."""

        alp_pk = self.kwargs.get("alp_pk", None)
        alp_instance = get_object_or_404(AdvancedLearningPath, pk=alp_pk)

        return alp_instance.related_advanced_learning_path_resources.all()
