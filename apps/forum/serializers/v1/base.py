from rest_framework import serializers

from apps.common.models.base import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.meta.models.hashtag import Hashtag


class CommonForumCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Common Forum serializer holds create, update & destroy."""

    hashtag = serializers.ListField(
        child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, required=False)
    )

    def validate(self, attrs):
        """Overriden to change the values of hashtag attribute."""

        if hashtags := attrs.get("hashtag"):
            hashtag_ids = [Hashtag.objects.get_or_create(name=hashtag)[0].id for hashtag in hashtags]
            attrs["hashtag"] = hashtag_ids
        return attrs

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["hashtag"] = self.instance.hashtag_as_name
        return meta


class CommonForumDetailSerializer(AppReadOnlyModelSerializer):
    """Common Retrieve serializer for forum."""

    hashtag = serializers.ListField(source="hashtag_as_name", read_only=True)
