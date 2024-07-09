from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, CreationAndModificationModel


class Trainer(CreationAndModificationModel):
    """
    Trainer model for IIHT-B2B.

    ********************* Model Fields *********************
    PK          - id
    FK          - created_by, modified_by
    M2M         - course, learning_pat, alp
    Unique      - uuid
    Fields      - first_name, last_name
    Json        - skills,
    Numeric     - trainer_id
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta:
        default_related_name = "related_trainers"

    course = models.ManyToManyField("learning.course", blank=True)
    learning_path = models.ManyToManyField("learning.LearningPath", blank=True)
    alp = models.ManyToManyField("learning.AdvancedLearningPath", blank=True)
    first_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    last_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    trainer_id = models.IntegerField()  # TODO: need to change this field as unique
    skills = models.JSONField()
