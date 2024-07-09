from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class CommonConfigFKModel(BaseModel):
    """
    Common Configuration model for YAKSHA & MML.

    ********************* Model Fields *********************
        PK          - id
        FK          - catalogue, course, learning_path, alp, skill_traveller, assignment
        Unique      - uuid, ss_id
        Numeric     - allowed_attempts, pass_percentage,
        Datetime    - created_at, modified_at
        Bool        - is_default
    """

    class Meta(BaseModel.Meta):
        abstract = True

    catalogue = models.ForeignKey(
        "learning.Catalogue", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    course = models.ForeignKey("learning.Course", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(
        "learning.LearningPath", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    alp = models.ForeignKey(
        "learning.AdvancedLearningPath", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    skill_traveller = models.ForeignKey(
        "learning.SkillTraveller", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    playground = models.ForeignKey(
        "learning.Playground", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    assignment = models.ForeignKey(
        "learning.Assignment", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    assignment_group = models.ForeignKey(
        "learning.AssignmentGroup", **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.CASCADE
    )
    allowed_attempts = models.PositiveIntegerField()
    pass_percentage = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
