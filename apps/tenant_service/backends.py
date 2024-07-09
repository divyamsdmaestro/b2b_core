import psycopg2
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS


class BaseMultiTenantBackend:
    """
    Common multi-tenant database backend, handling class. Defines abstract
    and common methods to be implemented for various database types.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_database_connection(self):
        """Returns the database connection."""

        raise NotImplementedError

    def get_database_credentials(self):
        """Returns the database credentials."""

        default_db_credentials = settings.DATABASES[DEFAULT_DB_ALIAS]
        return {
            "user": default_db_credentials["USER"],
            "password": default_db_credentials["PASSWORD"],
            "host": default_db_credentials["HOST"],
            "port": default_db_credentials["PORT"],
            "database": default_db_credentials["NAME"],
        }

    def is_database_created(self, db_name: str) -> bool:
        """Checks if the given database is created or not."""

        raise NotImplementedError

    def create_database(self, db_name: str) -> None:
        """
        Creates the given database. Should be called post `self.is_database_created`.
        Or else this might throw errors, which should be handled by the caller.
        """

        raise NotImplementedError

    def check_and_create_database(self, db_name: str) -> bool:
        """
        Checks if the database is created or not, if not created, creates it.
        Returns boolean indicating if the database is newly created.

        If Returns True, then the database is created when called.
        If Returns False, then the database is already created.
        """

        if not self.is_database_created(db_name=db_name):
            self.create_database(db_name=db_name)
            return True
        return False


class PostgresDatabaseMultiTenantBackend(BaseMultiTenantBackend):
    """The multi-tenant backend to handle postgres based databases."""

    def create_database(self, db_name: str) -> None:
        """Create database."""

        connection = self.get_database_connection()
        connection.autocommit = True  # needed for write
        cursor = connection.cursor()

        cursor.execute(f"CREATE database {db_name};")
        connection.close()

    def is_database_created(self, db_name: str) -> bool:
        """Check if database is already present."""

        connection = self.get_database_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}';")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return bool(result)

    def get_database_connection(self):
        """Return connection to the db engine."""

        return psycopg2.connect(**self.get_database_credentials())
