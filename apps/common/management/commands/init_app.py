from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, OperationalError, close_old_connections, connections
from django.db.migrations.executor import MigrationExecutor

from apps.access_control.config import RoleTypeChoices
from apps.common.helpers import pause_thread
from apps.common.idp_service import IDPCommunicator
from apps.common.management.commands.base import AppBaseCommand
from apps.tenant.models import Tenant


class Command(AppBaseCommand):
    help = "Initializes the app by running the necessary initial commands."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.tenant_service.models import DatabaseRouter

        db_connection, migration = self.db_connection_and_migration_validation()
        if not db_connection:
            return False

        self.print_styled_message("\n** Checking For Pending Migrations... **")
        if migration:
            self.print_styled_message("\n** Running migrations on the default database... **")
            call_command("migrate", database=DEFAULT_DB_ALIAS)
            self.print_styled_message("** Successfully migrated default database. **", "SUCCESS")
        else:
            self.print_styled_message("** No pending migrations found. **", "SUCCESS")

        count = 0
        is_success = False
        while count < 3:
            try:
                auth_token = self.get_idp_admin_auth_token()  # IDP Super Admin Login to get access token
                self.get_or_create_default_tenant(auth_token)  # get or create `default` tenant
                self.create_django_admin(auth_token)  # Create superuser admin on App's `default` tenant
                is_success = True
                break
            except Exception:
                pause_thread(2)
            count += 1
            self.print_styled_message(f"Initialization Failed. Re-attempting count {count}.", "ERROR")

        if not is_success:
            return False

        self.print_styled_message("\n** Checking For Pending Migrations For Tenants... **")
        if migration:
            self.print_styled_message("\n** Running migrations for all the Tenants... **")
            for tracker in DatabaseRouter.objects.all():
                self.print_styled_message(f"\n** Running migrations for {tracker.tenant.db_name}... **")
                tracker.auto_setup_database()
                if tracker.tenant.tenancy_name != settings.APP_DEFAULT_TENANT_NAME:
                    close_old_connections()
            self.print_styled_message("** Successfully migrated all the Tenant databases. **", "SUCCESS")
        else:
            self.print_styled_message("** No Migrations Found. Skipping Migrations for Tenants. **", "SUCCESS")

    def db_connection_and_migration_validation(self):
        """Check if we are connected to the database"""

        self.print_styled_message("\n** Initial DB Connection Checking... **")
        try:
            connection = connections[DEFAULT_DB_ALIAS]
            connection.cursor()
        except OperationalError:
            self.print_styled_message("Couldn't connect to the database.  Make sure its running!", "ERROR")
            self.print_styled_message("Bailing...", "ERROR")
            return False, []
        self.print_styled_message("** DB Connection Established. **", "SUCCESS")

        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        applied_migrations = set(executor.loader.applied_migrations)
        pending_migrations = [migration for migration in targets if migration not in applied_migrations]
        return True, pending_migrations

    def get_idp_admin_auth_token(self):
        """Get the IDP Admin Auth Token."""

        self.print_styled_message("\n** App Super Admin IDP Log In. **")
        data = IDPCommunicator().post(
            url_path="/api/TokenAuth/Authenticate",
            data={
                "userNameOrEmailAddress": settings.IDP_ADMIN_EMAIL,
                "password": settings.IDP_ADMIN_PASSWORD,
                "rememberClient": True,
                # "tenancyName": settings.IDP_ADMIN_TENANCY_NAME,  # For Super Admin it's not required.
            },
        )
        if data.get("status_code") != 200:
            reason = data.get("reason")
            self.print_styled_message("Invalid IDP ADMIN Credentials. Exiting the process...", "ERROR")
            self.print_styled_message(f"Error: {reason}", "ERROR")
            raise ValueError("Error")

        self.print_styled_message("** Super Admin Login Successful **", "SUCCESS")
        return data["data"]["accessToken"]

    @staticmethod
    def get_default_tenant():
        """Returns the default tenant."""

        default_tenancy_name = settings.APP_DEFAULT_TENANT_NAME
        try:
            default_tenant = Tenant.objects.get(tenancy_name=default_tenancy_name)
        except Tenant.DoesNotExist:
            default_tenant: Tenant = Tenant.objects.create(
                name=default_tenancy_name,
                tenancy_name=default_tenancy_name,
            )
            default_tenant.related_tenant_domains.create(name=settings.APP_DEFAULT_TENANT_DOMAIN)
            default_tenant.setup_database_and_router(
                in_default=True,
                database_name=settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"],
            )
        return default_tenant

    def get_or_create_default_tenant(self, auth_token):
        """Get or Create the default b2b Tenant object."""

        self.print_styled_message("\n** Retrieving Default Tenant From IDP. **")
        data = IDPCommunicator().get(
            url_path="api/services/platform/Tenant/Get",
            token=auth_token,
            params={"Id": settings.IDP_B2B_TENANT_ID},
        )
        if data.get("status_code") != 200:
            reason = data.get("reason")
            self.print_styled_message("Invalid Authorization Or Invalid Tenant Id. Stopping...", "ERROR")
            self.print_styled_message(f"Error: {reason}", "ERROR")
            raise ValueError("Error")

        self.print_styled_message("** Retrieved Default Tenant From IDP Successfully **", "SUCCESS")
        self.print_styled_message("\n** App Default Tenant Creation/Updating... **")
        default_tenant = self.get_default_tenant()
        default_tenant.idp_id = settings.IDP_B2B_TENANT_ID
        default_tenant.domain = settings.APP_DEFAULT_TENANT_DOMAIN
        default_tenant.save()
        self.print_styled_message("** App Default Tenant Creation/Updating Finished. **", "SUCCESS")

    def get_admin_idp_id(self, auth_token):
        """Returns admin idp id retrieved from IDP."""

        self.print_styled_message("\n** Creating/Retrieving App Super Admin On IDP. **")
        credentials = settings.APP_SUPER_ADMIN
        data = IDPCommunicator().get(
            url_path="api/services/platform/User/GetTenantUserByNameAsync",
            token=auth_token,
            params={"tenantId": settings.IDP_B2B_TENANT_ID, "userName": credentials["email"]},
        )
        if data["status_code"] == 200:
            self.print_styled_message(
                "** App Super Admin already registered on IDP. Info retrieved successfully **", "SUCCESS"
            )
            return data["data"]["id"]

        self.print_styled_message("App Super Admin not registered on IDP. Registration is in process...", "warning")
        # create tenant admin
        payload = {
            "userId": 0,
            "tenantId": settings.IDP_B2B_TENANT_ID,
            "tenantDisplayName": settings.APP_DEFAULT_TENANT_NAME,
            "tenantName": settings.APP_DEFAULT_TENANT_NAME,
            "role": "TenantAdmin",
            "email": credentials["email"],
            "name": credentials["first_name"],
            "surname": "Tenant admin",
            "configJson": "string",
            "password": credentials["password"],
            "businessUnitName": "test",
            "userIdNumber": "string",
            "userGrade": "string",
            "isOnsiteUser": "yes",
            "managerName": "test",
            "managerEmail": "test@gmail.com",
            "managerId": 0,
            "organizationUnitId": 0,
        }
        admin_data = IDPCommunicator().post(
            url_path="api/services/platform/Tenant/GetOrOnboardUserAsync", data=payload, token=auth_token
        )
        if admin_data.get("status_code") != 200:
            reason = admin_data.get("reason")
            self.print_styled_message(
                "Invalid Authorization Or Issues in Super Admin User Creation. Stopping...", "ERROR"
            )
            self.print_styled_message(f"Error: {reason}", "ERROR")
            raise ValueError("Error")

        self.print_styled_message("** Successfully registered App Super Admin on IDP. **", "SUCCESS")
        return admin_data["data"]["userId"]

    def create_django_admin(self, auth_token):
        """Create a default super admin."""

        from apps.access_control.models import UserRole

        credentials = settings.APP_SUPER_ADMIN
        user_model = get_user_model()
        admin_idp_id = self.get_admin_idp_id(auth_token)
        UserRole.populate_default_user_roles()
        admin_role = UserRole.objects.filter(role_type=RoleTypeChoices.admin).first()

        self.print_styled_message("\n** Creating/Updating App Super Admin. **")
        if default_superuser := user_model.objects.filter(email=credentials["email"]).first():
            # user already exists save once more so if any changes in env file will auto reflect.
            default_superuser.first_name = credentials["first_name"]
            default_superuser.password = make_password(credentials["password"])
            default_superuser.idp_id = admin_idp_id
            default_superuser.roles.add(admin_role)
            default_superuser.save()
            self.print_styled_message("** App Super Admin already exists. Updated Successfully. **", "SUCCESS")
        else:
            user = user_model.objects.create_superuser(**credentials, idp_id=admin_idp_id)
            user.roles.add(admin_role)
            self.print_styled_message("** App Super Admin User Created Successfully. **", "SUCCESS")
