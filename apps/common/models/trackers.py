from django.db import models
from django.db.models import JSONField

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel


class Log(BaseModel):
    """
    Model to hold the apps log details. This contains data based on the type given.
    This is a general purpose log, and can be used for anything and everything.
    """

    data = JSONField()
    category = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
