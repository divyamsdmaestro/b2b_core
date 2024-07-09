from djchoices import ChoiceItem, DjangoChoices


class PowerBIRoleChoices(DjangoChoices):
    """Holds the choices of PowerBIRoleChoices."""

    # Course
    super_admin = ChoiceItem("super_admin", "Super Admin")
    tenant_admin = ChoiceItem("tenant_admin", "Tenant Admin")
    tenant_manager = ChoiceItem("tenant_manager", "Tenant Manager")
    tenant_user = ChoiceItem("tenant_user", "Tenant User")


class RLSRoleChoices(DjangoChoices):
    """Choices for RLS User roles. DAX configurations. Contact PowerBI team for user roles."""

    tenant_user = ChoiceItem("TENANT USER", "TENANT USER")
    tenant_manager = ChoiceItem("TENANT MANAGER", "TENANT MANAGER")
    tenant_admin = ChoiceItem("TEANANT ADMIN", "TEANANT ADMIN")
    tenant_admin_rb = ChoiceItem("TENANT ADMIN", "TENANT ADMIN")
