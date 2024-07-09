from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, CUDArchivableModel, NameModel


class PerformanceMetrix(CUDArchivableModel, NameModel):
    """
    Base model for skill, category & roles.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by,
        Fields      - uuid, name, description,
        Numeric     - no_of_course, no_of_lp, no_of_alp, no_of_tp, no_of_tpg, no_of_st, no_of_assignment
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted, is_draft, is_archive, is_popular, is_recommended

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(CUDArchivableModel.Meta):
        abstract = True

    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    no_of_course = models.PositiveIntegerField(default=0)
    no_of_lp = models.PositiveIntegerField(default=0)
    no_of_alp = models.PositiveIntegerField(default=0)
    no_of_tp = models.PositiveIntegerField(default=0)  # tp --> Techademy Playground
    no_of_tpg = models.PositiveIntegerField(default=0)  # tpg --> Techademy Playground Group
    no_of_st = models.PositiveIntegerField(default=0)  # st --> Skill Traveller
    no_of_assignment = models.PositiveIntegerField(default=0)
    no_of_assignment_group = models.PositiveIntegerField(default=0)

    # BooleanFields
    is_popular = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
