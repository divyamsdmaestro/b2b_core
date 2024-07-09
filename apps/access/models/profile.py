from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    NameModel,
)
from apps.learning.config import ProficiencyChoices


class UserEducationDetail(NameModel):
    """
    Model to store educational details for user.
    Model Fields -
        PK          - id,
        FK          - education_type
        Fields      - uuid, name, university, degree
        Datetime    - created_at, modified_at, deleted_at
    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(NameModel.Meta):
        default_related_name = "related_user_education_details"

    education_type = models.ForeignKey(
        "meta.EducationType", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    university = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    degree = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)


class UserSkillDetail(BaseModel):
    """
    Model to store user skill details.

    Model Fields -
        PK          - id
        FK          - skill
        Fields      - uuid
        choices     - proficiency
        Datetime    - created_at, modified_at, deleted_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_user_skill_details"

    # Fk fields
    skill = models.ForeignKey(to="learning.CategorySkill", on_delete=models.CASCADE)

    # Choices
    proficiency = models.CharField(
        choices=ProficiencyChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        default=ProficiencyChoices.basic,
    )
