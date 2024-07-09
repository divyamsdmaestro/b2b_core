from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class BaseCourseEvaluationModel(BaseModel):
    """
    Common model for IIHT-Course assessments & assignments.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    FK          - module, course,
    Numeric     - sequence
    Datetime    - created_at, modified_at

    """

    class Meta(BaseModel.Meta):
        abstract = True

    module = models.ForeignKey(
        "learning.CourseModule", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    course = models.ForeignKey("learning.Course", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    sequence = models.PositiveIntegerField(default=0)
