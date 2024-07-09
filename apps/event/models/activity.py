from django.conf import settings
from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    CreationAndModificationModel,
    NameModel,
)
from apps.event.config import (
    ActivityTypeChoices,
    CalendarEventTypeChoices,
    EndTypeChoices,
    RemainderChoices,
    RepeatEveryTypeChoices,
    RepeatTypeChoices,
    UserStatusChoices,
    UserVisibilityChoices,
)


class CalendarActivity(CreationAndModificationModel, NameModel):
    """
    Activity model for IIHT-B2B calendar.

    ********************* Model Fields *********************

    PK          - id
    FK          - created_by, modified_by, user,
    Unique      - uuid
    Choices     - activity_type, repeat_type, repeat_every_type, ends_type,
                  user_status, user_visibility, notify, event_subtype
    Fields      - repeat_on, description, event_subtype_id
    Numeric     - repeat_occurrence_no, ends_after
    Datetime    - created_at, modified_at
    Date        - activity_date, ends_on
    Time        - from_time, to_time
    Bool        - is_auto_decline

    """

    class Meta:
        default_related_name = "related_calendar_activities"

    # FK
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    # Choices
    activity_type = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=ActivityTypeChoices.choices)
    event_subtype = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=CalendarEventTypeChoices.choices,
        default=CalendarEventTypeChoices.not_selected,
    )
    event_subtype_id = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    repeat_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=RepeatTypeChoices.choices,
        default=RepeatTypeChoices.does_not_repeat,
    )
    repeat_every_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=RepeatEveryTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    ends_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=EndTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    user_status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=UserStatusChoices.choices, default=UserStatusChoices.busy
    )
    user_visibility = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=UserVisibilityChoices.choices,
        default=UserVisibilityChoices.default_visibility,
    )
    notify = models.IntegerField(choices=RemainderChoices.choices, default=RemainderChoices.thirty_min_before)

    # CharFields & TextFields
    repeat_on = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # NumericFields
    repeat_occurrence_no = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ends_after = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Boolean Fields
    is_auto_decline = models.BooleanField(default=False)

    # DateTimeFields
    activity_date = models.DateField()
    ends_on = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    from_time = models.TimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    to_time = models.TimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def get_repeat_on(self):
        """Returns the list of repeat_on days."""

        if not self.repeat_on:
            return None
        return self.repeat_on.split(",")


class CalendarActivityTrackingModel(BaseModel):
    """
    Tracking model for calendar activity.

    ********************* Model Fields *********************

    PK          - id
    FK          - created_by, modified_by,
    Unique      - uuid
    Datetime    - created_at, modified_at

    """

    class Meta:
        default_related_name = "related_calendar_activity_trackers"

    activity = models.ForeignKey(to="event.CalendarActivity", on_delete=models.CASCADE)
    date = models.DateField()
    is_deleted = models.BooleanField(default=False)
