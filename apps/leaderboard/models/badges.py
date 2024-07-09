from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    CUDArchivableModel,
)
from apps.leaderboard.config import BadgeCategoryChoices, BadgeLearningTypeChoices, BadgeTypeChoices
from apps.learning.config import BadgeProficiencyChoices


class Badge(CUDArchivableModel):
    """
    Model to Store Badges Metadata.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by,
        Fields      - uuid, category, proficiency, type, from_range, to_range, points,
        Datetime    - created_at, modified_at, deleted_at,
        Bool        - is_deleted, is_active

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(CUDArchivableModel.Meta):
        default_related_name = "related_badges"

    # Fields
    category = models.CharField(choices=BadgeCategoryChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    type = models.CharField(choices=BadgeTypeChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    proficiency = models.CharField(
        choices=BadgeProficiencyChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    points = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    from_range = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    to_range = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def __str__(self):
        """`Milestone` with points as a string representation."""

        return f"{self.category} - {self.type}"


class BadgeActivity(BaseModel):
    """
    Model to Store Badge Activity.

    ********************* Model Fields *********************

        PK          - id,
        FK          - user, badge,
        Fields      - learning_type, learning_id, points, data
        Datetime    - created_at, modified_at,
        Bool        - is_ccms_obj

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(CUDArchivableModel.Meta):
        default_related_name = "related_badge_activities"

    # FK Fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    learning_type = models.CharField(
        choices=BadgeLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    learning_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    tracker_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    points = models.PositiveIntegerField(default=0)
    data = models.JSONField(default=dict)
    is_ccms_obj = models.BooleanField(default=False)

    def __str__(self):
        """User as string rep."""

        return self.user.name
