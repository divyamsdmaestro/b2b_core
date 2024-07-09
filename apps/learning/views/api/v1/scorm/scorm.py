from rest_framework.decorators import action

from apps.common.helpers import unpack_dj_choices
from apps.common.serializers import BaseIDNameSerializer
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.learning.config import BaseUploadStatusChoices
from apps.learning.helpers import scorm_upload_helper
from apps.learning.models import Scorm
from apps.learning.serializers.v1 import ScormCUDModelSerializer, ScormListSerializer
from apps.meta.models import Vendor
from apps.tenant_service.middlewares import get_current_db_name


class ScormUploadApiView(AppAPIView):
    """Api view to upload the scorm."""

    serializer_class = ScormCUDModelSerializer

    def post(self, request, *args, **kwargs):
        """Overriden to handle multiple scorm file uploads."""

        db_name = get_current_db_name()
        serializer = self.get_valid_serializer()
        files = serializer.validated_data.pop("files")
        vendor = serializer.validated_data.pop("vendor")
        for file in files:
            instance = Scorm.objects.create(name=file.name.split(".")[0], vendor=vendor)
            scorm_upload_helper(file=file, db_name=db_name, instance_id=instance.id)
            instance.upload_status = BaseUploadStatusChoices.initiated
            instance.save()
        return self.send_response("Scorm upload is in progress.")


class ScormUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to update and delete the scorm."""

    serializer_class = ScormCUDModelSerializer
    queryset = Scorm.objects.all()


class ScormListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the scorm."""

    serializer_class = ScormListSerializer
    queryset = Scorm.objects.all().order_by("created_at")
    search_fields = ["name"]
    filterset_fields = ["vendor", "upload_status"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        vendor = BaseIDNameSerializer(Vendor.objects.all(), many=True).data
        upload_status = unpack_dj_choices(BaseUploadStatusChoices.choices)
        return self.send_response(data={"vendor": vendor, "upload_status": upload_status})
