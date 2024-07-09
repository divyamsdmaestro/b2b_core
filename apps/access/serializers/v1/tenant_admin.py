"""
    Tenant Admin User creation helper serializer file.
    This is used while On-boarding of new Tenant to On-board Tenant specific user.
"""

from apps.access.models import User
from apps.access.models.user import UserDetail
from apps.common.serializers import AppCreateModelSerializer


class TenantAdminUserDetailCreateModelSerializer(AppCreateModelSerializer):
    """Create serializer class for tenant admin `UserDetail`."""

    class Meta(AppCreateModelSerializer.Meta):
        model = UserDetail
        fields = [
            "user_id_number",
            "user_grade",
            "is_onsite_user",
        ]


class TenantAdminUserCreateModelSerializer(AppCreateModelSerializer):
    """
    Create serializer class for tenant admin `User`.
    TODO: Everything should be a serializer field instead of model field.
     (model field might cause error due to uniqueness of field).
    """

    user_details = TenantAdminUserDetailCreateModelSerializer(read_only=False)

    class Meta(AppCreateModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "user_details",
        ]
