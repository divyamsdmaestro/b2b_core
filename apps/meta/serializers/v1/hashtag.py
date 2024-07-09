from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.meta.models import Hashtag


class HashtagCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Hashtag model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Hashtag
        fields = ["name"]
