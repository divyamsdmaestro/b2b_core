from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    NameModel,
    UniqueNameModel,
)
from apps.meta.config import FeedBackTypeChoices


class FeedbackTemplate(UniqueNameModel):
    """
    Feedback Model for IIHT-B2B

        PK       - id
        Fields   - uuid, name, description
        DateTime - created_at, modified_at

    """

    class Meta(UniqueNameModel.Meta):
        default_related_name = "related_feedback_templates"

    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class FeedbackTemplateQuestion(NameModel):
    """
    Model to store Feedback Quesitons related to Feedback Template

        PK       - id,
        FK       - feedback_template
        Fields   - uuid, name, question, response_type
        DateTime - created_at, modified_at


    """

    class Meta(NameModel.Meta):
        default_related_name = "related_template_questions"

    feedback_template = models.ForeignKey(to=FeedbackTemplate, on_delete=models.CASCADE)
    question = models.TextField()
    response_type = models.CharField(choices=FeedBackTypeChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class FeedbackTemplateChoice(NameModel):
    """
    Model to store Choices related to Feedback Questions

        PK       - id
        FK       - question
        Fields   - uuid, name, choice
        DateTime - created_at, modified_at


    """

    class Meta(NameModel.Meta):
        default_related_name = "related_question_choices"

    question = models.ForeignKey(to=FeedbackTemplateQuestion, on_delete=models.CASCADE)
    choice = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
