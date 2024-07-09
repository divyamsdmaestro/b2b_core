from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class BaseALPEvaluationModel(BaseModel):
    """
    Common model for IIHT-ALP assessments & assignments.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    FK          - alp_lp, alp,
    Numeric     - sequence
    Datetime    - created_at, modified_at
    """

    class Meta(BaseModel.Meta):
        abstract = True

    alp_lp = models.ForeignKey(
        "learning.ALPLearningPath", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    alp = models.ForeignKey(
        "learning.AdvancedLearningPath", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    sequence = models.PositiveIntegerField(default=0)
