from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import BaseLPEvaluationModel


class LPAssignment(BaseLPEvaluationModel):
    """
    Assignment model for IIHT-B2B learning_path & lp_courses.

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

    class Meta(BaseLPEvaluationModel.Meta):
        default_related_name = "related_lp_assignments"

    type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=CommonLearningAssignmentTypeChoices.choices
    )
    assignment = models.ForeignKey("learning.Assignment", on_delete=models.CASCADE)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the learning_path course count when the course is deleted."""

        instance = super().delete()
        if self.lp_course:
            self.lp_course.recalculate_lp_course_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        if self.learning_path:
            self.learning_path.recalculate_lp_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        return instance
