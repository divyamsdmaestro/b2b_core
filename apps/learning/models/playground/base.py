from django.db import models

from apps.learning.models import BaseRoleSkillLearningModel


class PlaygroundSkeletonModel(BaseRoleSkillLearningModel):
    """
    Base models for playground related models that contains basic fields.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - skill, role, forums, hashtag, feedback_template
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

    class Meta(BaseRoleSkillLearningModel.Meta):
        abstract = True

    # ManyToMany Field
    forums = models.ManyToManyField(to="forum.Forum", blank=True)
