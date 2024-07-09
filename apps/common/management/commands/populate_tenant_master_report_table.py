from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Populates the Master Report Details for Tenant."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.tenant.tasks import MasterReportTableTask

        tenant_id = input("Enter Tenant ID: ")
        self.print_styled_message(f"\n** Got Tenant ID {tenant_id}. **")
        MasterReportTableTask().run_task(tenant_id=tenant_id)
        self.print_styled_message(f"\n** Celery task called successfully for Tenant ID {tenant_id}. **")
