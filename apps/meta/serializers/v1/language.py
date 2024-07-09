from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.meta.models import Language


class LanguageCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Language model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Language
        fields = ["name"]
