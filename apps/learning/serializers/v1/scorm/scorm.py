from rest_framework import serializers

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.models import Scorm
from apps.learning.validators import validate_scorm_file_size, validate_zip_file
from apps.meta.models import Vendor


class ScormCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to upload scorms."""

    files = serializers.ListField(
        child=serializers.FileField(
            validators=[validate_scorm_file_size, validate_zip_file],
        ),
        required=False,
    )
    vendor = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    name = serializers.CharField(required=False)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Scorm
        fields = [
            "name",
            "vendor",
            "files",
        ]

    def validate(self, attrs):
        """Overriden to validate vendor and file fields."""

        if not self.instance:
            if not attrs.get("files"):
                raise serializers.ValidationError({"files": "This field is required."})
            elif len(attrs["files"]) > 3:
                raise serializers.ValidationError({"files": "You are allowed to upload maximum three files only."})
        elif attrs.get("files"):
            attrs.pop("files")
        vendor = Vendor.objects.filter(name=attrs["vendor"]).first()
        if not vendor:
            vendor = Vendor.objects.create(name=attrs["vendor"])
        attrs["vendor"] = vendor
        return attrs

    def get_meta_for_update(self, *args, **kwargs):
        """Overriden to add vendor details in initial data"""

        data = super().get_meta_for_update()
        data["initial"].update({"vendor": self.instance.vendor.name})
        return data


class ScormListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `Scorm` model."""

    vendor = BaseIDNameSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Scorm
        fields = [
            "id",
            "uuid",
            "name",
            "vendor",
            "file_url",
            "launcher_url",
            "upload_status",
            "reason",
        ]
