from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand
from apps.tenant_service.middlewares import set_db_for_router


class Command(AppBaseCommand):
    help = "Update or Create a PowerBI Report Details."
    ReportModel = None

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        self.ReportModel = apps.get_model("dashboard", "PowerBIDetail")

        is_copy_purpose = input("Enter 1 (To just populate to all tenants), 2 (skip & continue): ")
        if int(is_copy_purpose) == 1:
            tenant_id = input("Enter Tenant ID (Ignore for all): ")
            return self.populate_to_all_tenants(tenant_id=tenant_id)
        report_id = input("Enter Report ID (UUID): ")
        report_name = input("Enter Report Name: ")
        embed_url = input("Enter EmbedURL: ")
        dataset_id = input("Enter DatasetId (UUID): ")
        dataset_workspace_id = input("Enter Dataset Workspace Id (UUID): ")
        access_role = input("Enter Access Role (Case Sensitive): ")
        web_url = input("Enter WebURL (Not Required): ")

        self.print_styled_message(f"** Updating / Creating PowerBI Report with id - {report_id}. **\n")
        set_db_for_router()
        self.ReportModel.objects.update_or_create(
            report_id=report_id,
            defaults={
                "access_role": access_role,
                "report_name": report_name,
                "embed_url": embed_url,
                "dataset_id": dataset_id,
                "dataset_workspace_id": dataset_workspace_id,
                "web_url": web_url,
            },
        )
        self.print_styled_message("** Finished Creating / Updating PowerBI Report.", "SUCCESS")

    def populate_to_all_tenants(self, tenant_id=None):
        """Copy from default_tenant and populate to all other tenants."""

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        set_db_for_router()
        all_reports = {}
        for item in self.ReportModel.objects.active():
            # Assuming report_id is unique in powerbi model.
            all_reports[f"{item.report_id}"] = {
                "access_role": str(item.access_role),
                "report_name": str(item.report_name),
                "embed_url": str(item.embed_url),
                "dataset_id": str(item.dataset_id),
                "dataset_workspace_id": str(item.dataset_workspace_id),
                "web_url": str(item.web_url),
            }

        if tenant_id:
            self.print_styled_message(f"\n** Got Tenant ID {tenant_id}. **")
            tracker = DatabaseRouter.objects.get(tenant_id=tenant_id)
            self.populate_to_tenant(tracker, all_reports)
        else:
            self.print_styled_message("\n** Executing for all DBs. **")
            for tracker in DatabaseRouter.objects.all():
                self.populate_to_tenant(tracker, all_reports)

    def populate_to_tenant(self, tracker, report_data):
        """Populate all powerBI reports to the specific tenant."""

        self.print_styled_message(f"\n** Populating PowerBI Report for {tracker.database_name}. **")
        tracker.add_db_connection()
        db_name = str(tracker.database_name)
        set_db_for_router(db_name)
        # Assuming report_id is unique in powerbi model.
        for report_id, values in report_data.items():
            self.ReportModel.objects.update_or_create(
                report_id=report_id,
                defaults={
                    "access_role": values["access_role"],
                    "report_name": values["report_name"],
                    "embed_url": values["embed_url"],
                    "dataset_id": values["dataset_id"],
                    "dataset_workspace_id": values["dataset_workspace_id"],
                    "web_url": values["web_url"],
                },
            )
            self.print_styled_message(f"\n** Finished Populating for {db_name}. **")
