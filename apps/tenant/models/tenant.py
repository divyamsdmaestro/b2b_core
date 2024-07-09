from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, models

from apps.common.helpers import random_letters, random_n_strong_token
from apps.common.model_fields import AppPhoneNumberField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    ArchivableModel,
    CUDArchivableModel,
    CUDSoftDeleteModel,
    ImageOnlyModel,
    UniqueNameModel,
)
from apps.learning.config import BaseUploadStatusChoices


class TenantLogo(ImageOnlyModel):
    """
    Image data for a `Tenant`.

    Model Fields -
        PK          - id
        Fields      - uuid, image
        Datetime    - created_at, modified_at
    """

    pass


class TenantBanner(ImageOnlyModel):
    """
    BannerImage data for a `Tenant`.

    Model Fields -
        PK          - id
        Fields      - uuid, image
        Datetime    - created_at, modified_at
    """

    pass


class Tenant(ArchivableModel, UniqueNameModel):
    """
    Tenant model for IIHT-B2B. As per their current db structure.

    Model Fields -
        PK          - id,
        Fields      - uuid, name, tenancy_name, contact_number, email, image, idp_id, domain, data,
                        client_id, sso_tenant_id, secret_id, secret_value
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted, is_keycloak

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_tenants"

    # FK Fields
    logo: TenantLogo = models.ForeignKey(
        "tenant.TenantLogo", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Fields
    tenancy_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    custom_tenant_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    contact_number = AppPhoneNumberField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    idp_id = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    mml_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    data = models.JSONField(default=dict)
    issuer_url = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    client_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    sso_tenant_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    secret_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    secret_value = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    allowed_login_domain = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    api_secret_key = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_domain_restricted_login = models.BooleanField(default=False)
    is_keycloak = models.BooleanField(default=False)

    @property
    def file_url(self):
        """Returns the URL of the image."""

        return self.logo.file_url if self.logo else None

    @property
    def db_name(self):
        """Returns the db name. DRY & adaptor function."""

        try:
            return self.related_db_router.database_name
        except Exception:
            return None

    @property
    def db_status_label(self):
        """Returns the db status. DRY & adaptor function."""

        try:
            return BaseUploadStatusChoices.get_choice(self.related_db_router.setup_status).label
        except Exception:
            return "Database Router is not yet created."

    @property
    def db_status(self):
        """Returns the db status. DRY & adaptor function."""

        try:
            return BaseUploadStatusChoices.get_choice(self.related_db_router.setup_status).value
        except Exception:
            return BaseUploadStatusChoices.failed

    @property
    def db_router(self):
        """Returns the db status. DRY & adaptor function."""

        try:
            return self.related_db_router
        except Exception:
            return None

    @property
    def tenant_details(self):
        """Send minimal information about the tenant. Used in tenant service middleware."""

        try:
            config_model = self.related_tenant_configurations.first()
        except Exception:
            config_model = None
        data = {
            "id": self.pk,
            "uuid": self.uuid,
            "name": self.name,
            "tenancy_name": self.tenancy_name,
            "idp_id": self.idp_id,
            "db_name": self.db_name,
            "mml_id": self.mml_id,
            "sender_email": None,
            "wecp_key": None,
            "is_leaderboard_enabled": None,
            "is_self_enroll_enabled": None,
            "is_wecp_enabled": None,
            "is_mml_enabled": False,
            "issuer_url": self.issuer_url,
            "allowed_login_domain": self.allowed_login_domain,
            "is_domain_restricted_login": self.is_domain_restricted_login,
            "is_unlimited_users_allowed": True,
            "is_keycloak": self.is_keycloak,
        }
        if config_model:
            data["wecp_key"] = config_model.wecp_key
            data["yaksha_host"] = config_model.yaksha_host
            data["mml_host"] = config_model.mml_host
            data["virtutor_host"] = config_model.virtutor_host
            data["is_mml_enabled"] = config_model.is_mml_enabled
            data["is_leaderboard_enabled"] = config_model.is_leaderboard_enabled
            data["is_self_enroll_enabled"] = config_model.is_self_enroll_enabled
            data["is_wecp_enabled"] = config_model.is_wecp_enabled
            data["sender_email"] = config_model.sender_email
            data["is_chat_enabled"] = config_model.is_chat_enabled
            data["is_skill_traveller_enabled"] = config_model.is_skill_traveller_enabled
            data["is_mentor_enabled"] = config_model.is_mentor_enabled
            data["is_yaksha_enabled"] = config_model.is_yaksha_enabled
            data["is_forum_enabled"] = config_model.is_forum_enabled
            data["is_assignment_enabled"] = config_model.is_assignment_enabled
            data["is_assignment_group_enabled"] = config_model.is_assignment_group_enabled
            data["is_unlimited_users_allowed"] = config_model.is_unlimited_users_allowed
            data["allowed_user_count"] = config_model.allowed_user_count
            data["is_master_catalogue_enabled"] = config_model.is_master_catalogue_enabled
            data["is_skill_ontology_enabled"] = config_model.is_skill_ontology_enabled
        return data

    @property
    def tenant_config(self):
        """Return the tenant configuration instance."""

        config = TenantConfiguration.objects.filter(tenant=self).first()
        if not config:
            config = self.related_tenant_configurations.create()
        return config

    def activate_db(self):
        """Used in shell purpose only."""

        from apps.tenant_service.models import set_db_as_env

        # TODO: Optimize this, there is 2 times we are hitting dbrouter tabler.

        self.db_router.add_db_connection()
        return set_db_as_env(self.db_name)

    def deactivate_db(self):
        """Used in shell purpose only."""

        from apps.tenant_service.middlewares import set_db_for_router

        return set_db_for_router()

    def setup_database_and_router(self, in_default=False, **kwargs):
        """
        Called when the tenant is initially created. Sets up the database & routing handling.

        kwargs -
            database_user=,
            database_password=,
            database_host=,
            database_port=,
        """

        from apps.tenant_service.models import DatabaseRouter

        # setup database router for tenant
        if in_default:
            db_credentials = settings.DATABASES[DEFAULT_DB_ALIAS]
            kwargs["database_user"] = db_credentials["USER"]
            kwargs["database_password"] = db_credentials["PASSWORD"]
            kwargs["database_host"] = db_credentials["HOST"]
            kwargs["database_port"] = db_credentials["PORT"]
        if not (db_name := kwargs.get("database_name")):
            db_name = "".join(letter for letter in f"{self.tenancy_name}" if letter.isalnum()) + random_letters()
        kwargs["database_name"] = db_name.lower()
        router = DatabaseRouter.objects.create(tenant=self, **kwargs)
        # init database router
        router.setup_database()
        return router

    def apply_pre_populations(self):
        """
        Once tenant is created pre-populate some of the necessary data.
        Note: Order should not change Or Discuss before change.
        """

        from apps.access_control.models import PolicyCategory, UserRole
        from apps.tenant_service.middlewares import set_db_for_router

        if self.db_status == BaseUploadStatusChoices.completed:
            UserRole.populate_default_user_roles(db_name=self.db_name)
            set_db_for_router()
            PolicyCategory.populate_policies(db_name=self.db_name)
            set_db_for_router(self.db_name)

    def generate_api_secret(self):
        """Function to generate and replace API Secret Key for the tenant."""

        self.api_secret_key = random_n_strong_token(n=32)
        self.save()


class TenantConfiguration(CUDSoftDeleteModel):
    """
    Domain model for IIHT-B2B. Need to have this model has django_tenants library depends on it.

    Model Fields -
        PK          - id
        FK          - tenant, user, created_by, modified_by, deleted_by
        Fields      - uuid, config_type, config_str, allowed_user_count
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_leaderboard_enabled, is_deleted, is_self_enroll_enabled, is_unlimited_users_allowed,
                      is_chat_enabled, is_skill_traveller_enabled, is_mentor_enabled, is_yaksha_enabled,
                      is_forum_enabled, is_mml_enabled, is_master_catalogue_enabled

    App QuerySet Manager Methods -
        get_or_none, alive, dead, delete, hard_delete
    """

    class Meta(CUDSoftDeleteModel.Meta):
        default_related_name = "related_tenant_configurations"

    # FK fields
    tenant = models.ForeignKey("tenant.Tenant", on_delete=models.CASCADE)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # FK Fields
    banner_image: TenantBanner = models.ForeignKey(
        "tenant.TenantBanner", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Fields
    wecp_key = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    yaksha_host = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    mml_host = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    virtutor_host = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    sender_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    footer_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    config_type = models.PositiveSmallIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    config_str = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Added this field coz in sql server its str. After data migration process it and remove it.

    # Bool fields
    is_leaderboard_enabled = models.BooleanField(default=True)
    is_self_enroll_enabled = models.BooleanField(default=True)
    is_chat_enabled = models.BooleanField(default=True)
    is_skill_traveller_enabled = models.BooleanField(default=True)
    is_mentor_enabled = models.BooleanField(default=True)
    is_yaksha_enabled = models.BooleanField(default=True)
    is_wecp_enabled = models.BooleanField(default=False)
    is_forum_enabled = models.BooleanField(default=True)
    is_mml_enabled = models.BooleanField(default=True)
    is_assignment_enabled = models.BooleanField(default=False)
    is_assignment_group_enabled = models.BooleanField(default=False)
    is_unlimited_users_allowed = models.BooleanField(default=True)
    is_master_catalogue_enabled = models.BooleanField(default=True)
    is_skill_ontology_enabled = models.BooleanField(default=False)

    allowed_user_count = models.IntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class TenantDomain(CUDArchivableModel, UniqueNameModel):
    """
    Domain model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, deleted_by, tenant,
        Fields      - uuid, name,
        Datetime    - created_at, modified_at, deleted_at,
        Bool        - is_deleted, is_active,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(CUDArchivableModel.Meta):
        default_related_name = "related_tenant_domains"

    tenant = models.ForeignKey("tenant.Tenant", on_delete=models.CASCADE)
