from rest_framework.decorators import action

from apps.common.helpers import unpack_dj_choices
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelListAPIViewSet, get_upload_api_view
from apps.learning.config import LearningUpdateTypeChoices
from apps.learning.models import LearningUpdate, LearningUpdateImageModel
from apps.learning.serializers.v1 import LearningUpdateCUDModelSerializer, LearningUpdateListSerializer

LearningUpdateImageUploadAPIView = get_upload_api_view(
    meta_model=LearningUpdateImageModel, meta_fields=["id", "image"]
)


class LearningUpdateCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete LearningUpdates."""

    serializer_class = LearningUpdateCUDModelSerializer
    queryset = LearningUpdate.objects.all()


class LearningUpdateListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Learning Updates."""

    queryset = LearningUpdate.objects.all()
    serializer_class = LearningUpdateListSerializer
    filterset_fields = ["update_type", "course", "learning_path", "advanced_learning_path", "skill_traveller"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        update_type = self.serializer_class().serialize_dj_choices(LearningUpdateTypeChoices.choices)
        return self.send_response(data={"update_type": update_type})


class LearningUpdateTypeListAPIView(AppAPIView):
    """Api view to list the learning update types with count."""

    def get(self, *args, **kwargs):
        """Returns the list of update types."""

        query_params = self.request.query_params
        learning_type = query_params.get("learning_type")
        learning_id = query_params.get(learning_type)
        learning_update_objs = LearningUpdate.objects.filter(**{learning_type: learning_id})
        update_types = unpack_dj_choices(LearningUpdateTypeChoices.choices)
        for update_type in update_types:
            update_type["count"] = learning_update_objs.filter(update_type=update_type["id"]).count()
        return self.send_response(data={"update_type": update_types})
