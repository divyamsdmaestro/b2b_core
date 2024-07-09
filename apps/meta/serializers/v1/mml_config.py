from rest_framework import serializers

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import (
    AllowedFileExtensionChoices,
    AllowedFileNumberTypeChoices,
    AllowedSubmissionChoices,
    SubmissionTypeChoices,
)
from apps.meta.models import MMLConfiguration

COMMON_CONFIG_FIELDS = [
    "catalogue",
    "course",
    "learning_path",
    "alp",
    "skill_traveller",
    "playground",
    "assignment",
    "assignment_group",
    "pass_percentage",
    "allowed_attempts",
    "is_default",
]

MML_CONFIG_FIELDS = COMMON_CONFIG_FIELDS + [
    "submission_type",
    "files_allowed",
    "allowed_submission",
    "extensions_allowed",
    "max_files_allowed",
]


class CommonMMLConfigCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Common CUD model serializer for mml configurations."""

    extensions_allowed = serializers.MultipleChoiceField(
        choices=AllowedFileExtensionChoices.choices, source="extensions_allowed_as_list"
    )

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = MMLConfiguration
        fields = [
            "submission_type",
            "files_allowed",
            "allowed_submission",
            "extensions_allowed",
            "allowed_attempts",
            "max_files_allowed",
        ]

    def get_meta(self) -> dict:
        """Returns the metadata."""
        return {
            "submission_type": self.serialize_dj_choices(SubmissionTypeChoices.choices),
            "files_allowed": self.serialize_dj_choices(AllowedFileNumberTypeChoices.choices),
            "allowed_submission": self.serialize_dj_choices(AllowedSubmissionChoices.choices),
            "extensions_allowed": self.serialize_dj_choices(AllowedFileExtensionChoices.choices),
        }

    def get_dynamic_render_config(self):
        """Overridden to change the `extension_allowed` field config."""

        render_config = super().get_dynamic_render_config()
        for data in render_config:
            if data["key"] == "extensions_allowed":
                data["type"] = "ArrayField"
        return render_config

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["extensions_allowed"] = self.instance.extensions_allowed_as_list
        return meta


class MMLConfigCUDModelSerializer(CommonMMLConfigCUDModelSerializer):
    """CUD model serializer for MML configuration."""

    class Meta(CommonMMLConfigCUDModelSerializer.Meta):
        model = MMLConfiguration
        fields = MML_CONFIG_FIELDS


class MMLConfigListModelSerializer(AppReadOnlyModelSerializer):
    """List model serializers for MML configuration."""

    extensions_allowed = serializers.ListField(
        source="extensions_allowed_as_list",
        child=serializers.CharField(min_length=3, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, required=False),
        default=[],
        required=False,
        read_only=True,
    )

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = MMLConfiguration
        fields = ["id"] + MML_CONFIG_FIELDS
