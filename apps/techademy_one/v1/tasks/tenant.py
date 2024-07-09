import uuid

from apps.common.tasks import BaseAppTask
from apps.learning.config import BaseUploadStatusChoices


class T1TenantSetupTask(BaseAppTask):
    """Task to to create tenant triggered from Techademy One."""

    def run(self, tenant_id):
        """Run handler."""

        from apps.access_control.models import PolicyCategory, UserRole
        from apps.tenant.models import Tenant

        self.switch_db()
        tenant: Tenant = Tenant.objects.get(id=tenant_id)
        self.logger.info(f"Got T1TenantSetupTask for Tenant - {tenant.name}.")

        data = tenant.data["tenant_setup_data"]
        if not data:
            return False, "tenant_setup_data is missing"

        self.setup_tenant_address(tenant, data["address"])
        router = tenant.setup_database_and_router(in_default=True)
        if router.setup_status != BaseUploadStatusChoices.completed:
            return False

        UserRole.populate_default_user_roles(db_name=tenant.db_name)
        PolicyCategory.populate_policies(db_name=tenant.db_name)
        self.switch_db(router.database_name)
        self.setup_tenant_admin(data["tenantAdmin"], UserRole)
        return True

    @staticmethod
    def setup_tenant_address(tenant, address_data):
        """Create Address for Tenant."""

        from apps.meta.models import City, Country, State
        from apps.tenant.models import TenantAddress

        address_uuid, pincode = address_data["id"], address_data["pincode"]
        address_line_one, address_line_two = address_data["address_line_one"], address_data["address_line_two"]
        country, state, city = address_data["country"], address_data["state"], address_data["city"]

        try:
            country_obj = Country.objects.get(name__iexact=country)
        except Country.DoesNotExist:
            country_obj = Country.objects.create(name=country)
        try:
            state_obj = State.objects.get(name__iexact=state)
        except State.DoesNotExist:
            state_obj = State.objects.create(name=state, country=country_obj)
        try:
            city_obj = City.objects.get(name__iexact=city)
        except City.DoesNotExist:
            city_obj = City.objects.create(name=city, state=state_obj)

        if TenantAddress.objects.filter(uuid=address_uuid).first():
            address_uuid = uuid.uuid4()
        address = TenantAddress.objects.create(
            uuid=address_uuid,
            tenant=tenant,
            country=country_obj,
            state=state_obj,
            city=city_obj,
            address_line_one=address_line_one,
            address_line_two=address_line_two,
            pincode=pincode,
        )
        return address

    @staticmethod
    def setup_tenant_admin(admin_data_list, UserRole):
        """Create Admin for Tenant."""

        from apps.access.models import User, UserDetail
        from apps.access_control.config import RoleTypeChoices

        admin_role = UserRole.objects.filter(role_type=RoleTypeChoices.admin).first()

        for admin_data in admin_data_list:
            admin_uuid = admin_data.get("user_id", None)
            if not admin_uuid or User.objects.filter(uuid=admin_uuid).first():
                admin_uuid = uuid.uuid4()
            user = User.objects.create_superuser(
                uuid=admin_uuid,
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"],
                email=admin_data["email"],
            )
            UserDetail.objects.create(user=user, contact_number=admin_data["contact_number"])
            user.roles.add(admin_role)
            user.save()
        return True
