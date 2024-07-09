from rest_framework import serializers

from apps.common.serializers import BaseIDNameSerializer
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.meta.models import FeedbackTemplate
from apps.meta.serializers.v1 import FeedbackCUDSerializer, FeedbackRetrieveSerializer


class FeedbackTemplateCUDApiViewset(AppModelCUDAPIViewSet):
    """CUD Viewset for Admin Feedback Template"""

    queryset = FeedbackTemplate.objects.all()
    serializer_class = FeedbackCUDSerializer


class FeedbackTemplateListApiViewset(AppModelListAPIViewSet):
    """List Viewset to get all Feedback Template"""

    class _Serializer(BaseIDNameSerializer):
        """Serializer class for Feedback Template"""

        description = serializers.CharField()

    queryset = FeedbackTemplate.objects.all()
    serializer_class = _Serializer
    search_fields = ["name"]


class FeedbackTemplateRetrieveApiViewset(AppModelRetrieveAPIViewSet):
    """Detail Viewset for Admin Feedback Template"""

    queryset = FeedbackTemplate.objects.all()
    serializer_class = FeedbackRetrieveSerializer
