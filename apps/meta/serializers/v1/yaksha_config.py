from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import AssessmentResultTypeChoices
from apps.meta.models import YakshaConfiguration
from apps.meta.serializers.v1 import COMMON_CONFIG_FIELDS

COMMON_YAKSHA_CONFIG_FIELDS = COMMON_CONFIG_FIELDS + [
    "aeye_proctoring_config",
    "duration",
    "result_type",
    "negative_score_percentage",
    "window_violation_limit",
    "is_shuffling_enabled",
    "is_plagiarism_enabled",
    "is_proctoring_enabled",
    "is_full_screen_mode_enabled",
    "is_window_violation_restricted",
    "is_aeye_proctoring_enabled",
    "is_practice",
]


class CommonYakshaCreateModelSerializer(AppWriteOnlyModelSerializer):
    """Common create model serializer."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = YakshaConfiguration
        fields = [
            "allowed_attempts",
            "pass_percentage",
            "duration",
            "result_type",
            "is_shuffling_enabled",
        ]


class YakshaConfigCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Yaksha config model CUD serializer."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = YakshaConfiguration
        fields = COMMON_YAKSHA_CONFIG_FIELDS

    def get_meta(self) -> dict:
        """Returns the metadata."""

        meta = super().get_meta()
        meta["result_type"] = self.serialize_dj_choices(AssessmentResultTypeChoices.choices)
        return meta


class YakshaConfigListModelSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = YakshaConfiguration
        fields = COMMON_YAKSHA_CONFIG_FIELDS + ["id", "created_at"]
