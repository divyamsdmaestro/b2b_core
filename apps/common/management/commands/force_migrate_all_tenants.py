from django.apps import apps
from django.conf import settings
from django.db import close_old_connections

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Run migrations on all `Tenants`."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")

        self.print_styled_message("\n** Running migrations for all the Tenants... **")
        for tracker in DatabaseRouter.objects.all():
            self.print_styled_message(f"\n** Running migrations for {tracker.tenant.db_name}... **")
            tracker.auto_setup_database()
            if tracker.tenant.tenancy_name != settings.APP_DEFAULT_TENANT_NAME:
                close_old_connections()
        self.print_styled_message("** Successfully migrated all the Tenant databases. **", "SUCCESS")
