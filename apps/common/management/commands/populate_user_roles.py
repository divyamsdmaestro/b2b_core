from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Populates the default UserRoles to all the tenants."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        UserRole = apps.get_model("access_control", "UserRole")
        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")

        tenant_idp_id = input("Enter Tenant IDP ID (Ignore for all): ")

        if tenant_idp_id:
            self.print_styled_message(f"\n** Got Tenant IDP ID {tenant_idp_id}. **\n")
            tracker = DatabaseRouter.objects.get(tenant__idp_id=tenant_idp_id)
            self.populate_user_roles_to_tenant(tracker, UserRole)
        else:
            self.print_styled_message("\n** Executing for all DBs. **\n")
            for tracker in DatabaseRouter.objects.all():
                self.populate_user_roles_to_tenant(tracker, UserRole)
        self.print_styled_message("\n** Finished Populating UserRoles. **\n", "SUCCESS")

    def populate_user_roles_to_tenant(self, tracker, UserRole):
        """Populate the User Roles to the given tenant's db name."""

        self.print_styled_message(f"\n** Populating UserRole for {tracker.database_name}. **")
        tracker.add_db_connection()
        UserRole.populate_default_user_roles(tracker.database_name)
