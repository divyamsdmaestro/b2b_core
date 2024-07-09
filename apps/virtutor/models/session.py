from django.db import models

from apps.access_control.config import RoleTypeChoices
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    CreationAndModificationModel,
)


class ScheduledSession(CreationAndModificationModel):
    """
    Scheduled session detail model for IIHT-B2B.

    ********************* Model Fields *********************
    PK          - id
    FK          - created_by, modified_by, module
    Unique      - uuid
    Fields      - session_title, session_code
    Numeric     - scheduled_id
    URL         - session_url, external_session_url, base_url
    Datetime    - created_at, modified_at, start_date, end_date

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta:
        default_related_name = "related_scheduled_sessions"

    user = models.ForeignKey(
        to="access.User",
        on_delete=models.CASCADE,
        related_name="related_user_scheduled_sessions",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    creator_role = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=RoleTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    module = models.ForeignKey("learning.CourseModule", on_delete=models.CASCADE)
    session_title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    recording_days = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    session_code = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    scheduled_id = models.IntegerField()
    session_url = models.URLField()
    external_session_url = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    base_url = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
