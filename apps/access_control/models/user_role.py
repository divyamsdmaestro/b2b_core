from django.db import DEFAULT_DB_ALIAS, models

from apps.access_control.config import RoleTypeChoices
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    ArchivableModel,
    CUDSoftDeleteModel,
    NameModel,
)
from apps.tenant_service.middlewares import set_db_for_router
from config import settings


class UserRole(CUDSoftDeleteModel, NameModel):
    """
    User Roles for IIHT.

    Model Fields -
        PK          - id
        FK          - created_by, modified_by, deleted_by
        Fields      - uuid, name, description, role_type
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_deleted

    App QuerySet Manager Methods -
        get_or_none, alive, dead, delete, hard_delete
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_user_roles"

    # Fields
    role_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=RoleTypeChoices.choices, default=RoleTypeChoices.learner
    )
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    @classmethod
    def populate_default_user_roles(cls, db_name=None):
        """Populate the default user roles for the given database."""

        if not db_name or db_name == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
            set_db_for_router()
        else:
            set_db_for_router(db_name)

        for role_value, role_label in RoleTypeChoices.values.items():
            if not UserRole.objects.filter(role_type=role_value).exists():
                UserRole.objects.create(name=role_label, role_type=role_value)
        return True
