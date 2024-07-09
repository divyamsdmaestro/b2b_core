from apps.learning.models import BaseAssessmentModel, BaseSTEvaluationModel


class STAssessment(BaseSTEvaluationModel, BaseAssessmentModel):
    """
    Assessment model for IIHT-B2B skill_traveller & courses.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    UUID        - assessment_uuid
    FK          - st_course, skill_traveller,
    Fields      - type, name
    Numeric     - sequence
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseSTEvaluationModel.Meta):
        default_related_name = "related_st_assessments"

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the skill_traveller course count when the course is deleted."""

        instance = super().delete()
        if self.st_course:
            self.st_course.recalculate_st_course_dependencies_sequence(from_sequence=self.sequence)
        if self.skill_traveller:
            self.skill_traveller.recalculate_st_dependencies_sequence(assessment=True, from_sequence=self.sequence)
        return instance
