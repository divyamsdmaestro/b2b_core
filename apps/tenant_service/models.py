import copy

from django.conf import settings
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, models

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel
from apps.learning.config import BaseUploadStatusChoices
from apps.tenant_service.backends import PostgresDatabaseMultiTenantBackend


def set_db_as_env(use_db):
    """Sets the given db as env, used in shell."""

    from apps.tenant_service.middlewares import set_db_for_router

    router = DatabaseRouter.objects.get(database_name=use_db)
    router.add_db_connection()
    set_db_for_router(use_db)


class DatabaseRouter(BaseModel):
    """
    Table to track which database belongs to which `Tenant`. This is the main
    table behind the logic and present in the `default` database.

    This is nothing but a routing table.
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_db_router"

    BACKEND = PostgresDatabaseMultiTenantBackend

    # to which tenant
    tenant = models.OneToOneField(to="tenant.Tenant", on_delete=models.CASCADE)

    # database credentials
    database_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    database_user = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    database_password = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    database_host = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    database_port = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    setup_status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=BaseUploadStatusChoices.choices,
        default=BaseUploadStatusChoices.initiated,
    )
    is_default = models.BooleanField(default=False)

    def __str__(self):
        """Name as String representation."""

        return self.database_name

    def add_db_connection(self):
        """Adds the current instance's database connection to the app's settings."""

        db_settings_template = copy.deepcopy(settings.DATABASES[DEFAULT_DB_ALIAS])
        db_settings_template.update(
            {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": self.database_name,
                "USER": self.database_user,
                "PASSWORD": self.database_password,
                "HOST": self.database_host,
                "PORT": self.database_port,
            }
        )
        settings.DATABASES[f"{self.database_name}"] = db_settings_template

    def setup_database(self):
        """
        Does the following steps:
            1. Adds the db to the `settings.DATABASES`
            2. Creates & Initializes the db if necessary(migrate).

        Uses the credentials defined in the instance. This function is called
        after this instance is created, on `Tenant` signup.
        """

        # common variables
        db_name = f"{self.database_name}"
        self.setup_status = BaseUploadStatusChoices.in_progress
        self.save()

        # create the database
        backend = self.BACKEND()
        backend.check_and_create_database(db_name=db_name)

        # add the necessary connections
        self.add_db_connection()

        # migrate the necessary tables
        try:
            call_command("migrate", database=db_name)
            self.setup_status = BaseUploadStatusChoices.completed
            self.save()
        except Exception:
            self.setup_status = BaseUploadStatusChoices.failed
            self.save()

    def auto_setup_database(self):
        """
        Does the following steps:
            1. Adds the db to the `settings.DATABASES`
            2. Creates & Initializes the db if necessary(migrate).

        Uses the credentials defined in the instance. This function is called
        after this instance is created, on `Tenant` signup.

        Note: If there any changes in setup database change it otherwise don't.
        """

        # common variables
        db_name = f"{self.database_name}"
        self.setup_status = BaseUploadStatusChoices.in_progress
        self.save()

        # create the database
        backend = self.BACKEND()
        backend.check_and_create_database(db_name=db_name)

        # add the necessary connections
        self.add_db_connection()

        # migrate the necessary tables
        call_command("migrate", database=db_name)
        self.setup_status = BaseUploadStatusChoices.completed
        self.save()

    def is_database_valid(self):
        """Returns if the database is present or not. Just an adaptor."""

        backend = self.BACKEND()
        return backend.is_database_created(db_name=f"{self.database_name}")
