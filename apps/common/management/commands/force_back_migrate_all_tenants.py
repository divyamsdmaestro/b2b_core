from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db import close_old_connections

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Running back migration on all `Tenants`."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")

        app_name = input("Enter the app name:")
        file_name = input("Enter the migration file name:")
        self.print_styled_message("\n** Running back migration for Default database... **")
        call_command("migrate", app_name, file_name)
        self.print_styled_message("** Successfully back migrated for Default database. **", "SUCCESS")
        self.print_styled_message("\n** Running back migration for all the Tenants... **")
        for tracker in DatabaseRouter.objects.all():
            self.print_styled_message(f"\n** Running back migrations for {tracker.tenant.db_name}... **")
            tracker.add_db_connection()
            call_command("migrate", app_name, file_name, database=tracker.database_name)
            if tracker.tenant.tenancy_name != settings.APP_DEFAULT_TENANT_NAME:
                close_old_connections()
        self.print_styled_message("** Successfully back migrated all the Tenant databases. **", "SUCCESS")
