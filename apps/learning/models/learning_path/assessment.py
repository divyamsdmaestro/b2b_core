from apps.learning.models import BaseAssessmentModel, BaseLPEvaluationModel


class LPAssessment(BaseLPEvaluationModel, BaseAssessmentModel):
    """
    Assessment model for IIHT-B2B learning_path & courses.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    UUID        - assessment_uuid
    FK          - lp_course, learning_path,
    Fields      - type, name
    Numeric     - sequence
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseLPEvaluationModel.Meta):
        default_related_name = "related_lp_assessments"

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the learning_path course count when the course is deleted."""

        instance = super().delete()
        if self.lp_course:
            self.lp_course.recalculate_lp_course_dependencies_sequence(from_sequence=self.sequence)
        if self.learning_path:
            self.learning_path.recalculate_lp_dependencies_sequence(assessment=True, from_sequence=self.sequence)
        return instance
