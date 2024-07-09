from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Auto Assigns the default Admin UserRoles to Admins of all the tenants."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.access_control.config import RoleTypeChoices
        from apps.tenant_service.middlewares import set_db_for_router

        User = apps.get_model("access", "User")
        UserRole = apps.get_model("access_control", "UserRole")
        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")

        for tracker in DatabaseRouter.objects.all():
            use_db = tracker.database_name
            self.print_styled_message(f"\n** Working on {use_db} DB. **")
            tracker.add_db_connection()
            UserRole.populate_default_user_roles(tracker.database_name)
            set_db_for_router(use_db)
            admin_role = UserRole.objects.filter(role_type=RoleTypeChoices.admin).first()
            users = User.objects.filter(is_staff=True)
            count = 0
            for user in users:
                user.roles.add(admin_role)
                count += 1
            self.print_styled_message(f"\n** Done on {use_db} DB. Assigned {count} admins. **")
            set_db_for_router()
        self.print_styled_message("\n** Finished Assigning Default Admin Role. **\n", "SUCCESS")
