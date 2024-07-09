from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, ImageOnlyModel
from apps.learning.managers import CategorySkillObjectManagerQueryset
from apps.learning.models import PerformanceMetrix


class CategorySkillImageModel(ImageOnlyModel):
    """
    Image model for CategorySkill.

    Model Fields -
        PK          - id,
        FK          - created_by
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class CategorySkill(PerformanceMetrix):
    """
    CategorySkill model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, deleted_by, image
        M2M         - category
        Fields      - uuid, name, description,
        Numeric     - no_of_course, no_of_lp, no_of_alp, no_of_tp, no_of_tpg, no_of_st, no_of_assignment
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted, is_draft, is_archive, is_popular, is_recommended

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete, skill_course_count_update,
        skill_learning_path_count_update, skill_advanced_learning_path_count_update

    """

    class Meta(PerformanceMetrix.Meta):
        default_related_name = "related_category_skills"

    # Manager
    objects = CategorySkillObjectManagerQueryset.as_manager()

    # FKs
    image = models.ForeignKey(
        to=CategorySkillImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        related_name="category_skill_image",
    )
    category = models.ManyToManyField(to="learning.Category")
