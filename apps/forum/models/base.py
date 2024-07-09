from django.db import models
from django.utils import timezone

from apps.common.models.base import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    BaseModel,
    CreationModel,
    CUDArchivableModel,
    CUDSoftDeleteModel,
    NameModel,
    UniqueNameModel,
)


class ForumBaseModel(CUDArchivableModel, UniqueNameModel):  # TODO: replace created_by field with user as FK
    """
    Base models for forum related models that contains common fields.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by
        Fields      - uuid, description
        Unique      - name
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    class Meta(CUDSoftDeleteModel.Meta):
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft deletes obj."""

        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()


class PostBaseModel(CreationModel, NameModel):  # TODO: replace created_by field with user as FK
    """
    Base models for forum post related models that contains common fields.

    ********************* Model Fields *********************
    PK -
        id
    FK -
        created_by
    Unique -
        uuid
    Char -
        name
    Datetime -
        created_at
        modified_at
    """

    class Meta(CUDSoftDeleteModel.Meta):
        abstract = True


class ForumCourseRelationModel(BaseModel):
    """
    Just a linker model between forum & course.

    Model Fields -

        PK          - id,
        Fk          - forum, course
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta:
        default_related_name = "related_forum_course_relations"

    forum = models.ForeignKey(to="forum.Forum", on_delete=models.CASCADE)
    course = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)
