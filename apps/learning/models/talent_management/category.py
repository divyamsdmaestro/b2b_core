from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, ImageOnlyModel
from apps.learning.models.talent_management.common import PerformanceMetrix


class CategoryImageModel(ImageOnlyModel):
    """
    Image model for Category.

    Model Fields -
        PK          - id,
        Fields      - uuid, image
        Datetime    - created_at, modified_at
        FK          - created_by

    """

    pass


class Category(PerformanceMetrix):
    """
    Category model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, deleted_by, image
        Fields      - uuid, name, description,
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted, is_draft, is_archive
        Numeric     - no_of_course, no_of_lp, no_of_alp, no_of_tp, no_of_tpg, no_of_st, no_of_assignment

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(PerformanceMetrix.Meta):
        default_related_name = "related_categories"

    image = models.ForeignKey(
        to=CategoryImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    def category_course_count_update(self):
        """Update the no of courses assigned to the category."""

        self.no_of_course = self.related_courses.alive().count()
        self.save()

    def category_learning_path_count_update(self):
        """Update the no of learning paths assigned to the category."""

        self.no_of_lp = self.related_learning_paths.alive().count()
        self.save()

    def category_advanced_learning_path_count_update(self):
        """Update the no of advanced learning paths assigned to the category."""

        self.no_of_alp = self.related_advanced_learning_paths.alive().count()
        self.save()
