from django.core.validators import MaxValueValidator
from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, CreationAndModificationModel
from apps.my_learning.config import LearningStatusChoices


class BaseTrackingModel(CreationAndModificationModel):
    """
    Base model for tracking.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, enrollment
        Fields      - uuid, ss_id, ccms_id
        Numeric     - completed_duration, progress,
        Bool        - is_completed, is_ccms_obj
        Datetime    - created_at, modified_at, completion_date

     App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(CreationAndModificationModel.Meta):
        abstract = True

    ccms_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    completed_duration = models.PositiveIntegerField(default=0)
    progress = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    is_completed = models.BooleanField(default=False)
    is_ccms_obj = models.BooleanField(default=False)
    completion_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class BaseUserTrackingModel(BaseTrackingModel):
    """
    Base model for user tracking.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, enrollment, user
        Fields      - uuid, ss_id, ccms_id
        Numeric     - completed_duration, progress
        Bool        - is_completed, is_ccms_obj,
        Datetime    - last_accessed_on, created_at, modified_at, completion_date

     App QuerySet Manager Methods -
        get_or_none,
    """

    # TODO: Need to remove the null config for enrollment & user.

    class Meta(BaseTrackingModel.Meta):
        abstract = True

    enrollment = models.ForeignKey(
        to="my_learning.Enrollment", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    user = models.ForeignKey(to="access.User", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    @classmethod
    def get_default_report_data(cls):
        """Function to get the default report data if tracker is not available. Just a DRY stuff."""

        return {
            "video_progress": None,
            "start_date": None,
            "completion_date": None,
            "learning_status": LearningStatusChoices.not_started,
        }


class BaseAssessmentTrackingModel(CreationAndModificationModel):
    """
    Base Tracker model for IIHT-B2B assessments.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by,
        Fields      - uuid, ss_id, ccms_id
        Numeric     - progress, available_attempt
        Bool        - is_pass, is_completed, is_ccms_obj
        Datetime    - created_at, modified_at, start_date, completion_date, last_accessed_on

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(CreationAndModificationModel.Meta):
        abstract = True

    ccms_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    allowed_attempt = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    available_attempt = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    reattempt_count = models.PositiveIntegerField(default=0)
    assessment_uuid = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    progress = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    is_completed = models.BooleanField(default=False)
    is_pass = models.BooleanField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_ccms_obj = models.BooleanField(default=False)
    completion_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    start_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
