from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from rest_framework import serializers

from apps.access.helpers import idp_user_onboard
from apps.access.models import User, UserDetail
from apps.access.tasks import AutoAssignLearningTask
from apps.access_control.models import UserGroup, UserRole
from apps.access_control.serializers.v1 import UserGroupReadOnlySerializer, UserRoleReadOnlyModelSerializer
from apps.common.idp_service import idp_admin_auth_token, idp_get_request
from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer
from apps.tenant.models import Tenant
from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_details, set_db_for_router
from config.settings import IDP_CONFIG


class UserDetailReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for the `UserDetail` model."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserDetail
        fields = [
            "user_id_number",
            "user_grade",
            "manager_name",
            "manager_email",
            "manager_two_email",
            "manager_three_email",
            "organization_unit_id",
            "business_unit_name",
            "manager_id",
            "employee_id",
            "employment_start_date",
            "job_description",
            "job_title",
            "department_code",
            "department_title",
            "employment_status",
            "config_str",
            "is_onsite_user",
            "promotion_date",
            "certifications",
        ]


class UserReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for the `User` model."""

    roles = UserRoleReadOnlyModelSerializer(many=True)
    user_details = UserDetailReadOnlyModelSerializer(source="related_user_details", read_only=True)
    user_group = serializers.SerializerMethodField()

    def get_user_group(self, user):
        """Returns the user group details associated with the user object."""

        return (
            UserGroupReadOnlySerializer(user.related_user_groups.first()).data
            if user.related_user_groups.first()
            else None
        )

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = [
            "id",
            "uuid",
            "idp_id",
            "name",
            "roles",
            "email",
            "user_details",
            "user_group",
            "is_active",
        ]


class UserDetailCreateModelSerializer(AppCreateModelSerializer):
    """Serializer class for the `UserDetail` model. For SA to include user details."""

    promotion_date = serializers.DateField(required=False, allow_null=True)
    certifications = serializers.CharField(required=False, allow_null=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = UserDetail
        fields = [
            "user_id_number",
            "user_grade",
            "employee_id",
            "employment_start_date",
            "job_description",
            "job_title",
            "department_code",
            "department_title",
            "employment_status",
            "manager_id",
            "manager_name",
            "manager_email",
            "manager_two_email",
            "manager_three_email",
            "business_unit_name",
            "config_str",
            "is_onsite_user",
            "promotion_date",
            "certifications",
        ]


class UserCreateModelSerializer(AppCreateModelSerializer):
    """`User` create serializer for Super Admin."""

    user_details = UserDetailCreateModelSerializer(read_only=False)
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.alive(), required=False, allow_null=True)
    user_groups = serializers.PrimaryKeyRelatedField(queryset=UserGroup.objects.all(), required=False, allow_null=True)
    last_name = serializers.CharField(required=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "roles",
            "user_details",
            "tenant",
            "user_groups",
        ]

    def validate(self, attrs):
        """Validate user email uniqueness based on tenant."""

        tenant = attrs.get("tenant", None)
        db = get_current_db_name()
        if db and db != settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"] and tenant:
            raise serializers.ValidationError({"email": "Tenant Admin cannot create users on another tenant."})

        tenant_details = get_current_tenant_details()
        self.context["tenant_details"] = tenant_details
        if tenant:
            router = tenant.related_db_router
            router.add_db_connection()
            self.context["tenant_details"] = tenant.tenant_details
            set_db_for_router(router.database_name)
        if (
            not tenant_details["is_unlimited_users_allowed"]
            and User.objects.all().count() >= tenant_details["allowed_user_count"]
        ):
            raise serializers.ValidationError({"users": "User limit reached"})
        email = attrs["email"]
        auth_token = idp_admin_auth_token(field="email", raise_drf_error=True)
        self.context["auth_token"] = auth_token
        success, data = idp_get_request(
            url_path=IDP_CONFIG["get_tenant_user_by_name_url"],
            auth_token=auth_token,
            params={"tenantId": tenant_details["idp_id"], "userName": email},
        )
        if not success and data["status_code"] != 204:
            raise serializers.ValidationError({"email": "IDP Connection Error"})
        return attrs

    def create(self, validated_data):
        """Create user for the specified tenant."""

        user_details = validated_data.pop("user_details")
        roles = validated_data.pop("roles", [])
        user_groups = validated_data.pop("user_groups")
        tenant = validated_data.pop("tenant", None)
        tenant_details = self.context["tenant_details"]
        auth_token = self.context["auth_token"]

        if tenant and tenant.tenancy_name != settings.APP_DEFAULT_TENANT_NAME:
            set_db_for_router(tenant_details["db_name"])

        user = User.objects.create_user(**validated_data)
        UserDetail.objects.create(**user_details, user=user)
        user.roles.add(*roles)
        if user_groups:
            user_groups.members.add(user)
        # create tenant user on IDP
        tenant_data = {
            "idp_id": tenant_details["idp_id"],
            "name": tenant_details["name"],
            "tenancy_name": tenant_details["tenancy_name"],
            "issuer_url": tenant_details.get("issuer_url"),
        }
        success, message = idp_user_onboard(user, tenant_data, auth_token)
        if not success:
            raise serializers.ValidationError({"email": message})
        if tenant_details["idp_id"] == 482:
            AutoAssignLearningTask().run_task(user_id=user.id, db_name=get_current_db_name())
        return user

    def get_meta(self) -> dict:
        """get meta and initial values."""

        return {
            "roles": self.serialize_for_meta(UserRole.objects.alive(), fields=["id", "name"]),
            "user_groups": self.serialize_for_meta(UserGroup.objects.alive(), fields=["id", "name"]),
            "tenant": self.serialize_for_meta(Tenant.objects.alive(), fields=["id", "name"]),
        }
