from django.db import models

from apps.common.models.base import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    ImageOnlyModel,
    NameModel,
)
from apps.learning.config import LearningUpdateTypeChoices
from apps.my_learning.config import BaseLearningTypeChoices


class LearningUpdateImageModel(ImageOnlyModel):
    """
    Image model for LearningUpdate.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class LearningUpdate(NameModel):
    """
    model to store learning updates for IIHT-B2B courses.

    ********************* Model Fields *********************
    PK       - id
    Fields   - uuid, name, description
    FK       - course, learning_path, advanced_learning_path, skill_traveller
    choice   - update_type, learning_type
    Datetime - created_at, modified_at
    """

    class Meta(NameModel.Meta):
        default_related_name = "related_learning_updates"

    # FK
    learning_update_image = models.ForeignKey(
        to=LearningUpdateImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    course = models.ForeignKey("learning.Course", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    learning_path = models.ForeignKey(
        "learning.LearningPath", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    advanced_learning_path = models.ForeignKey(
        "learning.AdvancedLearningPath", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    skill_traveller = models.ForeignKey(
        "learning.SkillTraveller", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # TextField
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Choices
    learning_type = models.CharField(
        choices=BaseLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    update_type = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=LearningUpdateTypeChoices.choices)
