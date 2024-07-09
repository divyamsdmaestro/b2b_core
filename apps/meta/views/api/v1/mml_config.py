from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.meta.models import MMLConfiguration
from apps.meta.serializers.v1 import MMLConfigCUDModelSerializer, MMLConfigListModelSerializer


class MMLConfigCUDModelApiViewSet(AppModelCUDAPIViewSet):
    """CUD api view for MML configuration."""

    serializer_class = MMLConfigCUDModelSerializer
    queryset = MMLConfiguration.objects.all()


class MMLConfigListModelApiViewSet(AppModelListAPIViewSet):
    """List api view for MML configuration."""

    serializer_class = MMLConfigListModelSerializer
    queryset = MMLConfiguration.objects.all()
    filterset_fields = [
        "course",
        "learning_path",
        "alp",
        "skill_traveller",
        "playground",
        "assignment",
        "assignment_group",
        "is_default",
    ]
