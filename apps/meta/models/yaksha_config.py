from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.learning.config import AssessmentResultTypeChoices
from apps.meta.models import CommonConfigFKModel


class YakshaConfiguration(CommonConfigFKModel):
    """
    Configuration model for YAKSHA assessments.

    ********************* Model Fields *********************
        PK          - id
        FK          - catalogue, course, learning_path, skill_traveller, assignment
        Unique      - uuid, ss_id
        Fields      - aeye_proctoring_config,
        Numeric     - allowed_attempts, pass_percentage, duration, result_type, negative_score_percentage
        Datetime    - created_at, modified_at
        Bool        - is_shuffling_enabled, is_plagiarism_enabled, is_proctoring_enabled, is_full_screen_mode_enabled,
                      is_window_violation_restricted, is_aeye_proctoring_enabled, is_default, is_practice
    """

    class Meta(CommonConfigFKModel.Meta):
        default_related_name = "related_yaksha_configurations"

    aeye_proctoring_config = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    duration = models.PositiveIntegerField()
    result_type = models.PositiveIntegerField(choices=AssessmentResultTypeChoices.choices)
    negative_score_percentage = models.IntegerField(default=0)
    window_violation_limit = models.IntegerField(default=0)
    is_shuffling_enabled = models.BooleanField(default=False)
    is_plagiarism_enabled = models.BooleanField(default=False)
    is_proctoring_enabled = models.BooleanField(default=False)
    is_full_screen_mode_enabled = models.BooleanField(default=False)
    is_window_violation_restricted = models.BooleanField(default=False)
    is_aeye_proctoring_enabled = models.BooleanField(default=False)
    is_practice = models.BooleanField(default=False)
