from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import BaseCourseEvaluationModel


class CourseAssignment(BaseCourseEvaluationModel):
    """
    Assignment model for IIHT-Course & modules.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    FK          - module, course, assignment,
    Choices      - type
    Numeric     - sequence
    Datetime    - created_at, modified_at

    """

    class Meta(BaseCourseEvaluationModel.Meta):
        default_related_name = "related_course_assignments"

    type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=CommonLearningAssignmentTypeChoices.choices
    )
    assignment = models.ForeignKey("learning.Assignment", on_delete=models.CASCADE)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the learning_path course count when the course is deleted."""

        instance = super().delete()
        if self.module:
            self.module.recalculate_module_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        if self.course:
            self.course.recalculate_course_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        return instance
