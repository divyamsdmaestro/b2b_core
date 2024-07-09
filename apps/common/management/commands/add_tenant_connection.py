from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Add tenant db connection to settings."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        self.print_styled_message("\n** Adding All Or Specific Databases Connections. **\n")
        # TODO: Input for specific database name.
        for router in DatabaseRouter.objects.all():
            self.print_styled_message(f"\n** Adding connection for tenant - {router.tenant.name}. **")
            router.add_db_connection()
        self.print_styled_message("\n** Added All Or Specific Databases. **\n", "SUCCESS")
