import json

from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH
from apps.learning.config import AllowedFileNumberTypeChoices, AllowedSubmissionChoices, SubmissionTypeChoices
from apps.meta.models import CommonConfigFKModel


class MMLConfiguration(CommonConfigFKModel):
    """
    Configuration model for MML.

    ********************* Model Fields *********************
        PK          - id
        FK          - catalogue, course, learning_path, skill_traveller, assignment
        Unique      - uuid, ss_id
        Fields      - submission_type, files_allowed, allowed_submission, extensions_allowed
        Numeric     - allowed_attempts, max_files_allowed,
        Datetime    - created_at, modified_at
        Bool        - is_default
    """

    class Meta(CommonConfigFKModel.Meta):
        default_related_name = "related_mml_configurations"

    submission_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=SubmissionTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    files_allowed = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=AllowedFileNumberTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    allowed_submission = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=AllowedSubmissionChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    extensions_allowed = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Numeric
    max_files_allowed = models.IntegerField(default=1)

    @property
    def extensions_allowed_as_list(self):
        """Convert from string to list of strings based on condition."""

        try:
            extensions_allowed = json.loads(f"{self.extensions_allowed}".strip()) if self.extensions_allowed else []
        except Exception:  # noqa
            extensions_allowed = [f"{self.extensions_allowed}".strip()] if self.extensions_allowed else []
        return extensions_allowed

    @extensions_allowed_as_list.setter
    def extensions_allowed_as_list(self, value):
        """extension_allowed is stored on DB as a text json of the list object."""

        # TODO: Received the choices as set need to clear this doubt.
        self.extensions_allowed = json.dumps(list(value))
