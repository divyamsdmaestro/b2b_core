from django.db import models

from apps.common.models.base import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    CreationAndModificationModel,
    NameModel,
)
from apps.learning.config import BaseUploadStatusChoices


class Scorm(CreationAndModificationModel, NameModel):
    """
    Scorm model for IIHT-B2B.

    Model Fields -
        PK          - id,
        FK          - created_by, modified_by,
        Fields      - uuid, name, vendor
        Choices     - upload_status
        Datetime    - created_at, modified_at
        URL         - launcher_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(CreationAndModificationModel.Meta):
        default_related_name = "related_scorms"

    # CHAR Fields
    vendor = models.ForeignKey("meta.Vendor", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    upload_status = models.CharField(choices=BaseUploadStatusChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    # URL Fields
    file_url = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    launcher_url = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Text fields
    reason = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_standard = models.BooleanField(default=True)  # True -> Scorm version 1.2 & False -> Scorm version > 1.2
