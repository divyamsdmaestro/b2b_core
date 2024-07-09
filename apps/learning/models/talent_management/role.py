from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    ImageOnlyModel,
)
from apps.learning.config import ProficiencyChoices
from apps.learning.managers import CategoryRoleObjectManagerQueryset
from apps.learning.models import PerformanceMetrix


class CategoryRoleImageModel(ImageOnlyModel):
    """
    Image model for CourseRole.

    Model Fields -
        PK          - id,
        FK          - created_by
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class CategoryRole(PerformanceMetrix):
    """
    CategoryRole model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, deleted_by, image
        M2M         - category
        Numeric     - no_of_course, no_of_lp, no_of_alp, no_of_tp, no_of_tpg, no_of_st, no_of_assignment
        Fields      - uuid, name, description, required_qualifications
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted, is_draft, is_archive

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete, role_course_count_update,
        role_learning_path_count_update, role_advanced_learning_path_count_update,

    """

    class Meta(PerformanceMetrix.Meta):
        default_related_name = "related_category_roles"

    # Manager
    objects = CategoryRoleObjectManagerQueryset.as_manager()

    # FKs
    image = models.ForeignKey(
        to=CategoryRoleImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    category = models.ManyToManyField(
        to="learning.Category",
    )

    # Fields
    required_qualifications = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class RoleSkillRelation(BaseModel):
    """
    Model for related skills for role.

    ********************* Model Fields *********************
    PK          - id
    FK          - role, skill,
    Unique      - uuid, ss_id,
    Fields      - required_proficiency
    Datetime    - created_at, modified_at

    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_role_skill_relations"

    role = models.ForeignKey(CategoryRole, on_delete=models.CASCADE)
    skill = models.ForeignKey("learning.CategorySkill", on_delete=models.CASCADE)
    required_proficiency = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=ProficiencyChoices.choices
    )
