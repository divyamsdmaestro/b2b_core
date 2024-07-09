from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel
from apps.learning.config import ExpertLearningTypeChoices
from apps.my_learning.config import ActionChoices


class Expert(BaseModel):
    """
    Model to Store learning experts.

    ********************* Model Fields *********************

        PK          - id,
        FK          - user, course, learning_path,
        Datetime    - created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_experts"

    # FK Fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE)
    course = models.ForeignKey(
        "learning.Course",
        on_delete=models.CASCADE,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.CASCADE,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    advanced_learning_path = models.ForeignKey(
        "learning.AdvancedLearningPath",
        on_delete=models.CASCADE,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # ChoiceFields
    learning_type = models.CharField(
        choices=ExpertLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    action = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=ActionChoices.choices, default=ActionChoices.approved
    )

    # TODO: This field should not be default True. Change it in next model changes and handle it in api.
    # Bool fields
    is_created_by_admin = models.BooleanField(default=True)
