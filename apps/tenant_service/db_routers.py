from django.db import DEFAULT_DB_ALIAS

from apps.tenant_service.middlewares import get_current_db_name


class AppDBRouter:
    """
    Router for routing the model actions to the necessary databases.

    Works based on two ways:
        1. The `use_db` value set on the local thread while login and request.
    """

    def db_for_read(self, model, **hints):
        """For read actions."""

        return get_current_db_name() or DEFAULT_DB_ALIAS

    def db_for_write(self, model, **hints):
        """For write actions."""

        return get_current_db_name() or DEFAULT_DB_ALIAS

    def allow_relation(self, *args, **kwargs):
        """Prevent unnecessary breakages."""

        return True

    def allow_syncdb(self, *args, **kwargs):
        """Prevent unnecessary breakages."""

        return None
