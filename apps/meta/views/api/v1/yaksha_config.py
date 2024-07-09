from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.meta.models import YakshaConfiguration
from apps.meta.serializers.v1 import YakshaConfigCUDModelSerializer, YakshaConfigListModelSerializer


class YakshaConfigCUDApiViewSet(AppModelCUDAPIViewSet):
    """Yaskha config CUD api view."""

    serializer_class = YakshaConfigCUDModelSerializer
    queryset = YakshaConfiguration.objects.all()


class YakshaConfigListApiViewSet(AppModelListAPIViewSet):
    """Api view to list yaksha configurations."""

    serializer_class = YakshaConfigListModelSerializer
    queryset = YakshaConfiguration.objects.all()
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
