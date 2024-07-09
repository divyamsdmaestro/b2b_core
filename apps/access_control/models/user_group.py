from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    ArchivableModel,
    CUDSoftDeleteModel,
    NameModel,
)


class UserGroup(CUDSoftDeleteModel, NameModel):
    """
    User Group table.

    Model Fields -
        PK          - id
        FK          - members, manager, created_by, modified_by, deleted_by
        Fields      - uuid, name, group_id
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_deleted

    App QuerySet Manager Methods -
        get_or_none, alive, dead, delete, hard_delete
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_user_groups"

    # FK fields
    members = models.ManyToManyField("access.User")
    manager = models.ForeignKey(
        to="access.User",
        on_delete=models.SET_NULL,
        related_name="related_manager_user_groups",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # Fields
    group_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    @property
    def members_count(self):
        """Count of users."""

        return self.members.count()

    @property
    def manager_email(self):
        """Returns the user group's manager email."""

        return self.manager.email if self.manager else None
