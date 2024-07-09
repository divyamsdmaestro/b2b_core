from apps.learning.config import PlaygroundGuidanceChoices, PlaygroundToolChoices, PlaygroundTypeChoices
from apps.learning.models import Playground
from apps.learning.serializers.v1 import (
    BaseLearningListModelSerializer,
    BaseLearningSkillRoleCUDModelSerializer,
    BaseLearningSkillRoleRetrieveModelSerializer,
)


class PlaygroundListModelSerializer(BaseLearningListModelSerializer):
    """Playground retrieve model serializer."""

    class Meta(BaseLearningListModelSerializer.Meta):
        model = Playground
        fields = BaseLearningListModelSerializer.Meta.fields + [
            "playground_type",
            "guidance_type",
            "tool",
        ]


class PlaygroundRetrieveSerializer(BaseLearningSkillRoleRetrieveModelSerializer):
    """playground retrieve model serializer."""

    class Meta(BaseLearningSkillRoleRetrieveModelSerializer.Meta):
        model = Playground
        fields = BaseLearningSkillRoleRetrieveModelSerializer.Meta.fields + [
            "playground_type",
            "guidance_type",
            "tool",
        ]


class PlaygroundCUDModelSerializer(BaseLearningSkillRoleCUDModelSerializer):
    """Serializer class to create Playground."""

    class Meta(BaseLearningSkillRoleCUDModelSerializer.Meta):
        model = Playground
        fields = BaseLearningSkillRoleCUDModelSerializer.Meta.fields + [
            "playground_type",
            "guidance_type",
            "tool",
        ]

    def get_meta(self) -> dict:
        """Get meta & initial values for playgrounds."""

        meta = super().get_meta()
        meta.update(
            {
                "playground_type": self.serialize_dj_choices(PlaygroundTypeChoices.choices),
                "guidance_type": self.serialize_dj_choices(PlaygroundGuidanceChoices.choices),
                "tool": self.serialize_dj_choices(PlaygroundToolChoices.choices),
            }
        )
        return meta
