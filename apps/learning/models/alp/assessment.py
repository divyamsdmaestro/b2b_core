from apps.learning.models import BaseALPEvaluationModel, BaseAssessmentModel


class ALPAssessment(BaseALPEvaluationModel, BaseAssessmentModel):
    """
    Assessment model for IIHT-B2B alp & lp.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    UUID        - assessment_uuid
    FK          - alp_lp, alp,
    Fields      - type, name
    Numeric     - sequence
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseALPEvaluationModel.Meta):
        default_related_name = "related_alp_assessments"

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the alp dependencies sequence when the dependencies deleted."""

        instance = super().delete()
        if self.alp_lp:
            self.alp_lp.recalculate_alp_lp_dependencies_sequence(from_sequence=self.sequence)
        if self.alp:
            self.alp.recalculate_alp_dependencies_sequence(assessment=True, from_sequence=self.sequence)
        return instance
