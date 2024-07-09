from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, NameModel, StatusModel
from apps.mailcraft.config import MailTypeChoices


class MailTemplate(StatusModel, NameModel):
    """
    Dynamic Template holder.

    Fields:
        - id, uuid, ss_id, name, type, content, is_active, created_at, modified_at

    Qs Manager Methods:
        - get_or_none, active, inactive
    """

    class Meta(StatusModel.Meta):
        default_related_name = "related_mail_templates"

    # Fields
    type = models.CharField(
        choices=MailTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    subject = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    content = models.TextField()
