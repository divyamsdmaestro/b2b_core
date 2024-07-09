from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    CUDArchivableModel,
)
from apps.leaderboard.config import MilestoneChoices
from apps.my_learning.config import AllBaseLearningTypeChoices


class Milestone(CUDArchivableModel):
    """
    Model to Store Leaderboard Meta data.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by,
        Fields      - uuid, name, points,
        Datetime    - created_at, modified_at, deleted_at,
        Bool        - is_deleted, is_active

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(CUDArchivableModel.Meta):
        default_related_name = "related_leaderboards"

    # Fields
    name = models.CharField(choices=MilestoneChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    points = models.PositiveIntegerField()

    def __str__(self):
        """`Milestone` with points as a string representation."""

        return f"{MilestoneChoices.get_choice(self.name).label} - {self.points}"


class LeaderboardActivity(BaseModel):
    """
    Model to Store Leaderboard Activity.

    ********************* Model Fields *********************

        PK          - id,
        FK          - user, milestone, course, learning_path,
        Datetime    - created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(CUDArchivableModel.Meta):
        default_related_name = "related_leaderboard_activities"

    # FK Fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    course = models.ForeignKey(
        "learning.Course",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    advanced_learning_path = models.ForeignKey(
        "learning.AdvancedLearningPath",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    forum = models.ForeignKey("forum.Forum", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    learning_type = models.CharField(
        choices=AllBaseLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    ccms_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_ccms_obj = models.BooleanField(default=False)
    ccms_data = models.JSONField(default=dict)
    points = models.PositiveIntegerField(default=0)

    @classmethod
    def find_or_create(cls, user, milestone, use_kwargs=None, **kwargs):
        """Find activity by milestone name instead of milestone id and create if activity not found."""

        if use_kwargs:
            try:
                activity = cls.objects.get(user=user, milestone__name=milestone.name, **kwargs)
                is_created = False
            except cls.DoesNotExist:
                activity = cls.objects.create(user=user, milestone=milestone, **kwargs)
                is_created = True
        else:
            try:
                activity = cls.objects.get(user=user, milestone__name=milestone.name)
                is_created = False
            except cls.DoesNotExist:
                activity = cls.objects.create(user=user, milestone=milestone)
                is_created = True
        return activity, is_created


class LeaderboardCompetition(BaseModel):
    """
    Model to Store Leaderboard Competition data for User.

    ********************* Model Fields *********************

        PK          - id,
        FK          - user, competitors,
        Datetime    - created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none
    """

    # FK Fields
    user = models.OneToOneField(
        "access.User", on_delete=models.CASCADE, related_name="related_leaderboard_competition"
    )
    competitors = models.ManyToManyField("access.User", related_name="related_leaderboard_competitors", blank=True)
