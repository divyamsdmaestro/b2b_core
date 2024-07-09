from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import BaseSTEvaluationModel


class STAssignment(BaseSTEvaluationModel):
    """
    Assignment model for IIHT-B2B skill_traveller & st_courses.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    FK          - module, course,
    Choices     - type
    Numeric     - sequence
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseSTEvaluationModel.Meta):
        default_related_name = "related_st_assignments"

    type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=CommonLearningAssignmentTypeChoices.choices
    )
    assignment = models.ForeignKey("learning.Assignment", on_delete=models.CASCADE)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the skill_traveller course count when the course is deleted."""

        instance = super().delete()
        if self.st_course:
            self.st_course.recalculate_st_course_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        if self.skill_traveller:
            self.skill_traveller.recalculate_st_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        return instance
