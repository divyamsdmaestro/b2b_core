from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor


def is_default_database_synchronized():
    """
    Checks if the default database is synchronized or migrated. Used
    to apply the necessary init settings.* configurations.
    """

    try:
        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        return not executor.migration_plan(targets)
    except Exception:
        return False


def add_all_db_connections_to_settings():
    """
    Called on the `config.urls`. When the app is started is called ONCE
    to add all the database connections to the settings.DATABASES.
    """

    if settings.MULTI_TENANT["APP_LOAD_ALL_DB_CONNECTION"]:
        from apps.tenant_service.models import DatabaseRouter

        for tracker in DatabaseRouter.objects.all():
            tracker.add_db_connection()
