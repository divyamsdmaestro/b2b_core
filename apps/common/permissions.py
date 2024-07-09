from rest_framework import permissions

# from apps.access_control.models import RolePermission


class PolicyPermission(permissions.BasePermission):
    """Custom Policy based permission."""

    def has_permission(self, request, view):
        """Get the policy slug from the view and validate permissions."""

        # policy_slug = view.policy_slug
        user = request.user
        if user.is_anonymous:
            return False
        return True
        # if user.is_superuser or not user.roles.exists():
        #     return True
        # if not user.current_role or user.current_role.role_type != "manager":
        #     return True
        #
        # try:
        #     role_permission = user.role.related_role_permissions.get(policy__slug=policy_slug)
        #     if view.action == "create":
        #         return role_permission.is_creatable
        #     elif view.action == "update":
        #         return role_permission.is_editable
        #     elif view.action in ["retrieve", "list"]:
        #         return role_permission.is_viewable
        #     elif view.action == "destroy":
        #         return role_permission.is_deletable
        # except RolePermission.DoesNotExist:
        #     pass
        # return False


class ExtTenantAPIAccessPermission(permissions.BasePermission):
    """Custom API KEY based access."""

    def has_permission(self, request, view):
        """Get the API KEY from request and validate access."""

        from apps.tenant.models import Tenant

        if token := request.headers.get("ext-api-token"):
            if tenant := Tenant.objects.get_or_none(api_secret_key=token):
                tenant.activate_db()
                return True
        return False
