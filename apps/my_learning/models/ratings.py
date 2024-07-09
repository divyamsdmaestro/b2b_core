from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.my_learning.config import RatingTypeChoices
from apps.my_learning.models import BaseLearningFKModel


class UserRating(BaseLearningFKModel):
    """Model to store user ratings for all the learning models."""

    class Meta(BaseLearningFKModel.Meta):
        default_related_name = "related_user_ratings"

    # Choices
    learning_type = models.CharField(
        choices=RatingTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    # Fields
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
