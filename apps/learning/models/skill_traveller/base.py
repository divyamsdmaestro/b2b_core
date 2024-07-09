from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class BaseSTEvaluationModel(BaseModel):
    """
    Common model for IIHT-ST assessments & assignments.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    FK          - st_course, skill_traveller,
    Numeric     - sequence
    Datetime    - created_at, modified_at
    """

    class Meta(BaseModel.Meta):
        abstract = True

    st_course = models.ForeignKey(
        "learning.SkillTravellerCourse", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    skill_traveller = models.ForeignKey(
        "learning.SkillTraveller", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    sequence = models.PositiveIntegerField(default=0)
