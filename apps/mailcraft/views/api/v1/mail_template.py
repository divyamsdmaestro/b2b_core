from apps.common.serializers import AppReadOnlyModelSerializer
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.mailcraft.models import MailTemplate
from apps.mailcraft.serializers.v1 import MailTemplateCUDModelSerializer, MailTemplateRetrieveModelSerializer


class MailTemplateCUAPIViewSet(AppModelCUDAPIViewSet):
    """View to handle `MailTemplate` CUD."""

    queryset = MailTemplate.objects.all()
    serializer_class = MailTemplateCUDModelSerializer


class MailTemplateListAPIViewSet(AppModelListAPIViewSet):
    """View to handle listing of the `MailTemplate` model."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Serializer class for the same view."""

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = MailTemplate
            fields = [
                "id",
                "uuid",
                "name",
                "type",
                "subject",
                "is_active",
                "created_at",
                "modified_at",
            ]

    serializer_class = _Serializer
    queryset = MailTemplate.objects.all().order_by("-created_at")
    filterset_fields = ["id", "name", "type", "is_active"]
    search_fields = ["name", "subject"]


class MailTemplateRetrieveAPIViewSet(AppModelRetrieveAPIViewSet):
    """View to handle `MailTemplate` model retrieve."""

    queryset = MailTemplate.objects.all()
    serializer_class = MailTemplateRetrieveModelSerializer
