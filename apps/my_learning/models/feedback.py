from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel
from apps.my_learning.config import AllBaseLearningTypeChoices


class FeedbackResponse(BaseModel):
    """
    Model to store User's Feedback Response

        PK - id,
        FK - user, template, question, choice
        DateTime - created_at, modified_at
        Fields - uuid, text

    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_feedback_responses"

    user = models.ForeignKey(to="access.User", on_delete=models.CASCADE)
    learning_type = models.CharField(
        choices=AllBaseLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    learning_type_id = models.CharField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    question = models.ForeignKey(
        to="meta.FeedbackTemplateQuestion", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    choice = models.ForeignKey(
        to="meta.FeedbackTemplateChoice", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_ccms_obj = models.BooleanField(default=False)
    template_ccms_id = models.CharField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    question_ccms_id = models.CharField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    choice_ccms_id = models.CharField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    text = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
