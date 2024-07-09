from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel
from apps.learning.config import LearningTypeChoices
from apps.learning.models import BaseLearningModel, BaseRoleSkillLearningModel


class LearningPathCommonModel(BaseRoleSkillLearningModel):
    """
    Base models for learning path related models that contains common fields.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency, learning_type
        Numeric     - rating, duration, certificate, learning_points,
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    # Fields
    learning_type = models.CharField(
        choices=LearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    class Meta(BaseRoleSkillLearningModel.Meta):
        abstract = True


class SkillRoleBaseModel(BaseLearningModel):
    """
    Base models for skill and role based learning.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - forums, hashtag, course, learning_path, advanced_learning_path, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
        Numeric     - rating, duration, certificate, learning_points,
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    course = models.ManyToManyField("learning.Course", blank=True)
    learning_path = models.ManyToManyField("learning.LearningPath", blank=True)
    advanced_learning_path = models.ManyToManyField("learning.AdvancedLearningPath", blank=True)

    class Meta(BaseLearningModel.Meta):
        abstract = True


class BaseLPEvaluationModel(BaseModel):
    """
    Common model for IIHT-LP assessments & assignments.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    FK          - lp_course, learning_path,
    Numeric     - sequence
    Datetime    - created_at, modified_at
    """

    class Meta(BaseModel.Meta):
        abstract = True

    lp_course = models.ForeignKey(
        "learning.LearningPathCourse", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    sequence = models.PositiveIntegerField(default=0)
