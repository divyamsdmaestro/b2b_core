from apps.learning.models import BaseAssessmentModel, BaseCourseEvaluationModel


class CourseAssessment(BaseCourseEvaluationModel, BaseAssessmentModel):
    """
    Assessment model for IIHT-B2B courses & modules.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    UUID        - assessment_uuid
    FK          - module, course,
    Fields      - type, name
    Numeric     - sequence
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseCourseEvaluationModel.Meta):
        default_related_name = "related_course_assessments"

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the learning_path course count when the course is deleted."""

        instance = super().delete()
        if self.module:
            self.module.recalculate_module_dependencies_sequence(assessment=True, from_sequence=self.sequence)
        if self.course:
            self.course.recalculate_course_dependencies_sequence(assessment=True, from_sequence=self.sequence)
        return instance
