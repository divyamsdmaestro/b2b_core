from copy import copy

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.db import DEFAULT_DB_ALIAS

from apps.access_control.config import RoleTypeChoices
from apps.common.config import DEFAULT_PASSWORD_LENGTH
from apps.common.helpers import random_n_token
from apps.common.idp_service import idp_admin_auth_token, idp_post_request
from apps.common.management.commands.base import AppBaseCommand
from config import settings
from config.settings import IDP_CONFIG


class Command(AppBaseCommand):
    help = "Create user for Tenant.."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.tenant_service.middlewares import set_db_for_router

        Tenant = apps.get_model("tenant", "Tenant")
        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        UserRole = apps.get_model("access_control", "UserRole")
        User = apps.get_model("access", "User")

        tenant_idp_id = int(input("Enter Tenant IDP ID (Ignore for all): "))
        user_first_name = input("Enter User First Name: ")
        user_last_name = input("Enter User Last Name: ")
        user_email = input("Enter User Email: ")
        user_password = input("Enter User Password (Ignore to auto generate): ")
        user_id_number = input("Enter User ID Number: ")
        user_role_type = str(input("Enter User Role to be assigned (Exact Name): ")).lower()

        tenant = Tenant.objects.get(idp_id=tenant_idp_id)
        self.print_styled_message(f"\n** Retrieved Tenant {tenant.name} with IDP Id {tenant_idp_id}. **")
        db_name = tenant.db_name
        tracker = DatabaseRouter.objects.get(database_name=db_name)
        self.print_styled_message("** Adding & Setting Tenant connection. **\n")
        tracker.add_db_connection()

        if not db_name or db_name == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
            set_db_for_router()
        else:
            set_db_for_router(db_name)

        idp_user_role = "TenantAdmin" if user_role_type == RoleTypeChoices.admin else "TenantUser"
        user_role = UserRole.objects.get(role_type=user_role_type)
        self.print_styled_message(f"\n** Retrieved User Role {user_role.name}. **\n")

        # Registering User on IDP
        self.print_styled_message("\n** Registering User On IDP. **")
        auth_token = idp_admin_auth_token(raise_drf_error=False)
        user_password_copied = copy(user_password)
        if not user_password:
            user_password = random_n_token(DEFAULT_PASSWORD_LENGTH)
            user_password_copied = copy(user_password)
        payload = {
            "userId": 0,
            "tenantId": tenant.idp_id,
            "tenantDisplayName": tenant.name,
            "tenantName": tenant.tenancy_name,
            "role": idp_user_role,
            "email": user_email,
            "name": user_first_name,
            "surname": user_last_name,
            "configJson": "string",
            "password": user_password_copied,
            "businessUnitName": "string",
            "userIdNumber": user_id_number,
            "userGrade": "string",
            "isOnsiteUser": "string",
            "managerName": "string",
            "managerEmail": "string",
            "managerId": 0,
            "organizationUnitId": 0,
        }
        success, data = idp_post_request(
            url_path=IDP_CONFIG["get_or_onboard_user_url"], data=payload, auth_token=auth_token
        )

        if not success:
            self.print_styled_message("** Error Registering User on IDP. **\n")
            raise ValueError("User IDP Registration Failed!")
        self.print_styled_message("** Successfully Registered User on IDP. **\n", "SUCCESS")
        self.print_styled_message(f"\n** Creating User on Tenant DB {db_name}")
        user = User.objects.create_user(
            first_name=user_first_name, last_name=user_last_name, email=user_email, idp_id=data["userId"]
        )
        user.roles.add(user_role)
        user.password = make_password(user_password_copied)
        user.save()
        self.print_styled_message("** Finished Creating User.", "SUCCESS")
        self.print_styled_message(f"** User Email: {user_email}, User Password: {user_password_copied}. **", "SUCCESS")
        self.print_styled_message(f"** Role assigned to User is {user_role.name}. **", "SUCCESS")
        self.print_styled_message("** Copy user password once lost it cannot be retrieved. **\n")
