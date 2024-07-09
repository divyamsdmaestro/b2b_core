from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Create database for tenants if it is not created."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        Tenant = apps.get_model("tenant", "Tenant")
        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")

        tenant_idp_id = input("Enter Tenant IDP ID (Ignore for all): ")
        if tenant_idp_id and int(tenant_idp_id):
            tenant = Tenant.objects.get(idp_id=int(tenant_idp_id))
            self.print_styled_message(f"\n** Got Tenant from IDP ID {tenant_idp_id} & Name = {tenant.name}. **")
            self.create_tenant_db(tenant, DatabaseRouter)
        else:
            self.print_styled_message("\n** Executing for all Tenants. **")
            for tenant in Tenant.objects.all():
                self.create_tenant_db(tenant, DatabaseRouter)
        self.print_styled_message("** Finished Creating Databases. **\n", "SUCCESS")

    def create_tenant_db(self, tenant, DatabaseRouter):
        """Create tenant db."""

        database_exists = DatabaseRouter.objects.filter(tenant=tenant).exists()
        if not database_exists:
            self.print_styled_message(f"\n** Creating database for tenant - {tenant.name}. **")
            tenant.setup_database_and_router(in_default=True)
            self.print_styled_message(f"** Finished Creating Database for {tenant.name}. **\n", "SUCCESS")
        else:
            self.print_styled_message(f"** Database Already Exists for {tenant.name}. **\n")
