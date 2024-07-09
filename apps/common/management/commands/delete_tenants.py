from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Deleting Tenant and Tenant Databases."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from django.db import connection

        from apps.tenant.models import Tenant

        tenant_ids = []
        tenants = Tenant.objects.exclude(id__in=tenant_ids)
        cursor = connection.cursor()
        for tenant in tenants:
            if tenant.db_name:
                cursor.execute(f"DROP DATABASE IF EXISTS {tenant.db_name};")
                self.print_styled_message(f"{tenant.db_name} db was deleted.")
            t_name = tenant.tenancy_name
            tenant.hard_delete()
            self.print_styled_message(f"{t_name} tenant was deleted.")
