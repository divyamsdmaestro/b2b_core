from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import BaseALPEvaluationModel


class ALPAssignment(BaseALPEvaluationModel):
    """
    Assignment model for IIHT-B2B alp & alp_lp.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    FK          - alp_lp, alp,
    Choices     - type
    Numeric     - sequence
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseALPEvaluationModel.Meta):
        default_related_name = "related_alp_assignments"

    type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=CommonLearningAssignmentTypeChoices.choices
    )
    assignment = models.ForeignKey("learning.Assignment", on_delete=models.CASCADE)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the alp dependencies sequence when the dependencies deleted."""

        instance = super().delete()
        if self.alp_lp:
            self.alp_lp.recalculate_alp_lp_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        if self.alp:
            self.alp.recalculate_alp_dependencies_sequence(assignment=True, from_sequence=self.sequence)
        return instance
