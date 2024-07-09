from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH
from apps.my_learning.config import FavouriteTypeChoices
from apps.my_learning.models import BaseLearningFKModel


class UserFavourite(BaseLearningFKModel):
    """Model to store user favourite."""

    class Meta(BaseLearningFKModel.Meta):
        default_related_name = "related_user_favourites"

    # FK fields
    category = models.ForeignKey(
        "learning.Category", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    skill = models.ForeignKey(
        "learning.CategorySkill", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    role = models.ForeignKey(
        "learning.CategoryRole", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Choices
    favourite_type = models.CharField(
        choices=FavouriteTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
