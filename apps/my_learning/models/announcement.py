from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    ImageOnlyModel,
)
from apps.my_learning.config import AnnouncementTypeChoices


class AnnouncementImageModel(ImageOnlyModel):
    """
    Image model for Announcement.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class Announcement(BaseModel):
    """
    Model to store Announcements

        PK - id,
        MtoM - user, user_group
        DateTime - created_at, modified_at
        Fields - uuid, text, type

    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_announcements"

    # FK Fields
    announcement_image = models.ForeignKey(
        to=AnnouncementImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # Char Fields
    title = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    type = models.CharField(
        choices=AnnouncementTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    # Text Fields
    text = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # MtoM Fields
    user_group = models.ManyToManyField("access_control.UserGroup", blank=True)
    user = models.ManyToManyField("access.User", blank=True)
