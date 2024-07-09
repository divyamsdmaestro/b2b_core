from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Populates the hardcoded policies to all the tenants."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        PolicyCategory = apps.get_model("access_control", "PolicyCategory")
        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")

        tenant_idp_id = input("Enter Tenant IDP ID (Ignore for all): ")

        if tenant_idp_id:
            self.print_styled_message(f"\n** Got Tenant IDP ID {tenant_idp_id}. **")
            tracker = DatabaseRouter.objects.get(tenant__idp_id=tenant_idp_id)
            self.populate_policies_to_tenant(tracker, PolicyCategory)
        else:
            self.print_styled_message("\n** Executing for all DBs. **")
            for tracker in DatabaseRouter.objects.all():
                self.populate_policies_to_tenant(tracker, PolicyCategory)
        self.print_styled_message("** Finished Populating Policies. **\n", "SUCCESS")

    def populate_policies_to_tenant(self, tracker, PolicyCategory):
        """Populate the policies to the given tenant's db name."""

        self.print_styled_message(f"\n** Populating policies for {tracker.database_name}. **")
        tracker.add_db_connection()
        PolicyCategory.populate_policies(tracker.database_name)
        self.print_styled_message(f"\n** Finished Populating Policies for {tracker.database_name}. **\n", "SUCCESS")
