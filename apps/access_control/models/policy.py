from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, models

from apps.access_control.fixtures import SHARED_POLICY_FIXTURE, SUPER_TENANT_POLICY_FIXTURE
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    ArchivableModel,
    CUDSoftDeleteModel,
    NameModel,
)
from apps.tenant_service.middlewares import set_db_for_router


class PolicyCategory(NameModel):
    """Dynamic creation of policy categories. This is a helper model to achieve the same."""

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_policy_categories"

    # Fields
    slug = models.SlugField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    @classmethod
    def populate_policies(cls, db_name=None):
        """Just a helper method to populate the policy categories and policies."""

        # TODO: Move this to task once celery is setup. Change according to per tenant db arch.

        fixtures = SHARED_POLICY_FIXTURE
        if not db_name or db_name == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
            fixtures.update(SUPER_TENANT_POLICY_FIXTURE)
            set_db_for_router()
        else:
            set_db_for_router(db_name)

        for policy_category, values in fixtures.items():
            policies = values.pop("policies")
            category = cls.objects.filter(slug=policy_category).first()
            if not category:
                category = cls.objects.create(slug=policy_category, name=values["name"])
            else:
                category.name = values["name"]
                category.save()
            values["policies"] = policies
            for policy in policies:
                if existing_policy := category.related_policies.filter(slug=policy["slug"]).first():
                    existing_policy.name = policy["name"]
                    existing_policy.description = policy.get("description") or policy["name"]
                    existing_policy.save()
                else:
                    category.related_policies.create(
                        name=policy["name"],
                        slug=policy["slug"],
                        description=policy.get("description") or policy["name"],
                    )


class Policy(NameModel):
    """Dynamic creation of policies. This is a helper model to achieve the same."""

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_policies"

    # FK Fields
    policy_category = models.ForeignKey(PolicyCategory, on_delete=models.CASCADE)

    # Fields
    slug = models.SlugField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class RolePermission(CUDSoftDeleteModel):
    """
    Dynamic creation of Role Permissions.

    Model Fields -
        PK          - id
        FK          - policy, created_by, modified_by, deleted_by
        Fields      - uuid,
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_creatable, is_viewable, is_editable, is_deletable, is_deleted

    App QuerySet Manager Methods -
        get_or_none, alive, dead, delete, hard_delete
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_role_permissions"

    # FK Fields
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    role = models.ForeignKey(to="access_control.UserRole", on_delete=models.CASCADE)

    # Bool Fields
    is_creatable = models.BooleanField(default=False)
    is_viewable = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=False)
    is_deletable = models.BooleanField(default=False)
