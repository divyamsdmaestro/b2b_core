from apps.learning.models import PlaygroundGroup
from apps.learning.serializers.v1 import (
    BaseLearningListModelSerializer,
    BaseLearningSkillRoleCUDModelSerializer,
    BaseLearningSkillRoleRetrieveModelSerializer,
)


class PlaygroundGroupListSerializer(BaseLearningListModelSerializer):
    """Playground group retrieve model serializer."""

    class Meta(BaseLearningListModelSerializer.Meta):
        model = PlaygroundGroup
        fields = BaseLearningListModelSerializer.Meta.fields + ["no_of_playgrounds"]


class PlaygroundGroupRetrieveSerializer(BaseLearningSkillRoleRetrieveModelSerializer):
    """playground group retrieve model serializer."""

    class Meta(BaseLearningSkillRoleRetrieveModelSerializer.Meta):
        model = PlaygroundGroup
        fields = BaseLearningSkillRoleRetrieveModelSerializer.Meta.fields + [
            "no_of_playgrounds",
        ]


class PlaygroundGroupCUDModelSerializer(BaseLearningSkillRoleCUDModelSerializer):
    """Serializer class to create Playground Group."""

    class Meta(BaseLearningSkillRoleCUDModelSerializer.Meta):
        model = PlaygroundGroup
        fields = BaseLearningSkillRoleCUDModelSerializer.Meta.fields
