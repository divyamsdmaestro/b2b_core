from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_ipv46_address
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.access.models import User
from apps.access.models.user import UserDetail
from apps.access.serializers.v1 import TenantAdminUserCreateModelSerializer
from apps.access_control.config import RoleTypeChoices
from apps.access_control.models import PolicyCategory, UserRole
from apps.common.idp_service import idp_admin_auth_token, idp_get_request, idp_post_request
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import (
    AppCreateModelSerializer,
    AppReadOnlyModelSerializer,
    AppUpdateModelSerializer,
    AppWriteOnlyModelSerializer,
    BaseIDNameSerializer,
    FileModelToURLField,
)
from apps.common.validators import ListUniqueValidator
from apps.tenant.models import Tenant
from apps.tenant.models.tenant import TenantBanner, TenantConfiguration, TenantDomain
from apps.tenant.validators import DatabaseNameValidator, DomainNameValidator
from apps.tenant_service.middlewares import set_db_for_router
from apps.tenant_service.models import DatabaseRouter
from config.settings import IDP_CONFIG


class TenantConfigurationRetrieveModelSerializer(AppReadOnlyModelSerializer):
    """TenantConfiguration Detail serializer."""

    user = BaseIDNameSerializer()
    tenant = BaseIDNameSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = TenantConfiguration
        fields = [
            "id",
            "uuid",
            "user",
            "tenant",
            "sender_email",
            "footer_email",
            "config_type",
            "config_str",
            "wecp_key",
            "is_leaderboard_enabled",
            "is_self_enroll_enabled",
            "is_chat_enabled",
            "is_skill_traveller_enabled",
            "is_mentor_enabled",
            "is_yaksha_enabled",
            "is_wecp_enabled",
            "is_forum_enabled",
            "is_mml_enabled",
            "is_assignment_enabled",
            "is_assignment_group_enabled",
            "is_master_catalogue_enabled",
            "is_skill_ontology_enabled",
            "is_unlimited_users_allowed",
            "allowed_user_count",
        ]


class TenantRetrieveModelSerializer(AppReadOnlyModelSerializer):
    """Tenant Detail serializer."""

    logo = FileModelToURLField()
    tenant_configuration = serializers.SerializerMethodField()

    def get_tenant_configuration(self, obj):
        """Retrieve the configuration details."""

        try:
            config = obj.related_tenant_configurations.latest("-created_at")
        except TenantConfiguration.DoesNotExist:
            config = None
        return TenantConfigurationRetrieveModelSerializer(config).data

    class Meta(AppCreateModelSerializer.Meta):
        model = Tenant
        fields = [
            "id",
            "uuid",
            "idp_id",
            "name",
            "tenancy_name",
            "custom_tenant_id",
            "contact_number",
            "email",
            "logo",
            "mml_id",
            "tenant_configuration",
        ]


class TenantConfigurationModelSerializer(AppWriteOnlyModelSerializer):
    """CUD serializer class for `TenantConfiguration`."""

    banner_image = serializers.PrimaryKeyRelatedField(
        queryset=TenantBanner.objects.all(), required=False, allow_null=True
    )
    sender_email = serializers.EmailField(required=False, allow_null=True)
    footer_email = serializers.EmailField(required=False, allow_null=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = TenantConfiguration
        fields = [
            "wecp_key",
            "is_leaderboard_enabled",
            "banner_image",
            "sender_email",
            "footer_email",
            "is_chat_enabled",
            "is_skill_traveller_enabled",
            "is_mentor_enabled",
            "is_wecp_enabled",
            "is_yaksha_enabled",
            "is_forum_enabled",
            "is_mml_enabled",
            "is_assignment_enabled",
            "is_assignment_group_enabled",
            "is_master_catalogue_enabled",
            "is_skill_ontology_enabled",
            "is_unlimited_users_allowed",
            "allowed_user_count",
        ]

    def validate(self, attrs):
        """Function to validate limited user count"""

        if not attrs["is_unlimited_users_allowed"] and not attrs["allowed_user_count"]:
            raise serializers.ValidationError({"allowed_user_count": "This field is required"})
        if attrs["is_wecp_enabled"] and not attrs["wecp_key"]:
            raise serializers.ValidationError({"wecp_key": "This field is required"})
        if attrs["is_unlimited_users_allowed"]:
            attrs["allowed_user_count"] = None
        return attrs


class TenantDatabaseRouterCreateModelSerializer(AppCreateModelSerializer):
    """Create serializer class for `DatabaseRouter`."""

    use_current_db = serializers.BooleanField(default=False)
    database_name = serializers.CharField(validators=[DatabaseNameValidator()])

    class Meta(AppCreateModelSerializer.Meta):
        model = DatabaseRouter
        fields = [
            "database_name",
            "database_user",
            "database_password",
            "database_host",
            "database_port",
            "use_current_db",
        ]
        extra_kwargs = {
            "database_user": {"allow_null": True, "allow_blank": True, "required": False},
            "database_password": {"allow_null": True, "allow_blank": True, "required": False},
            "database_host": {"allow_null": True, "allow_blank": True, "required": False},
            "database_port": {"allow_null": True, "allow_blank": True, "required": False},
        }

    def validate(self, attrs):
        """Custom Validation."""

        if not attrs.get("use_current_db", None):
            for field in self.fields:
                if field not in ["use_current_db", "database_name"] and not attrs.get(field, None):
                    raise serializers.ValidationError({field: "This field is required."})

        database_host = attrs.get("database_host", None)
        if database_host and database_host != "localhost":
            try:
                validate_ipv46_address(database_host)
            except DjangoValidationError as e:
                raise serializers.ValidationError("Enter a valid IP address.") from e
        return attrs


class TenantDomainListModelSerializer(AppReadOnlyModelSerializer):
    """List serializer class for `TenantDomain`."""

    class Meta:
        model = TenantDomain
        fields = [
            "id",
            "name",
            "uuid",
            "tenant",
            "is_active",
        ]


class TenantDomainCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Update serializer class for `TenantDomain`."""

    name = serializers.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        validators=[DomainNameValidator(), UniqueValidator(TenantDomain.objects.all())],
        required=True,
    )

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = TenantDomain
        fields = [
            "name",
            "tenant",
            "is_active",
        ]

    def get_meta(self) -> dict:
        """Get meta data."""

        return {"tenant": self.serialize_for_meta(Tenant.objects.alive(), fields=["id", "name"])}


class TenantDomainUniqueListSerializer(serializers.ListSerializer):
    """List serializer class to validate the domain name."""

    validators = [
        ListUniqueValidator(
            unique_field_names=["name"],
            error_message={
                "name": "Domain name already exists.",
            },
        )
    ]


class TenantDomainCreateModelSerializer(AppCreateModelSerializer):
    """CUD serializer class for `TenantDomain`."""

    name = serializers.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        validators=[DomainNameValidator(), UniqueValidator(TenantDomain.objects.all())],
        required=True,
    )

    class Meta(AppWriteOnlyModelSerializer.Meta):
        list_serializer_class = TenantDomainUniqueListSerializer
        model = TenantDomain
        fields = [
            "name",
        ]


class TenantCreateModelSerializer(AppCreateModelSerializer):
    """Create serializer class for `Tenant`."""

    tenant_configuration = TenantConfigurationModelSerializer(read_only=False)
    tenant_admin_details = TenantAdminUserCreateModelSerializer(read_only=False)
    tenant_db_router = TenantDatabaseRouterCreateModelSerializer(read_only=False)
    contact_number = PhoneNumberField(region="IN")
    tenant_domain = TenantDomainCreateModelSerializer(read_only=False, many=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = Tenant
        fields = [
            "name",
            "tenancy_name",
            "custom_tenant_id",
            "logo",
            "contact_number",
            "email",
            "issuer_url",
            "client_id",
            "sso_tenant_id",
            "secret_id",
            "secret_value",
            "tenant_configuration",
            "tenant_admin_details",
            "tenant_db_router",
            "tenant_domain",
            "mml_id",
            "allowed_login_domain",
            "is_domain_restricted_login",
        ]

    def validate_tenancy_name(self, tenancy_name):
        """Validate name is available on IDP and locally."""

        success, data = idp_post_request(
            url_path=IDP_CONFIG["tenant_availability_url"], data={"tenancyName": tenancy_name}
        )
        is_name_taken = Tenant.objects.filter(tenancy_name=tenancy_name).exists()
        if not success:
            raise serializers.ValidationError("IDP Connection Error")
        if is_name_taken or data.get("tenantId"):  # data.get("tenantId") will return id if idp tenant exists.
            raise serializers.ValidationError(f"The Name {tenancy_name} is already taken.")
        return tenancy_name

    def validate(self, attrs):
        """Validate if domains exists."""

        tenant_domain = attrs.get("tenant_domain", [])
        allowed_login_domain = attrs.get("allowed_login_domain")
        if not tenant_domain:
            raise serializers.ValidationError({"tenant_domain": "This field is required."})
        if attrs.get("is_domain_restricted_login") and not allowed_login_domain:
            raise serializers.ValidationError({"allowed_login_domain": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to create a new Tenant along with Tenant Admin."""

        tenant_configuration = validated_data.pop("tenant_configuration")
        tenant_admin_details = validated_data.pop("tenant_admin_details")
        admin_extra_details = tenant_admin_details.pop("user_details")
        tenant_db_router = validated_data.pop("tenant_db_router")
        tenant_domain = validated_data.pop("tenant_domain")
        use_current_db = tenant_db_router.pop("use_current_db", False)

        tenant = Tenant.objects.create(**validated_data)
        tenant.related_tenant_configurations.create(**tenant_configuration)
        for domain in tenant_domain:
            tenant.related_tenant_domains.create(**domain)
        router: DatabaseRouter = tenant.setup_database_and_router(in_default=use_current_db, **tenant_db_router)
        self.tenant_and_user_idp_registration(tenant_admin_details, admin_extra_details, tenant, router.database_name)
        return tenant

    @staticmethod
    def tenant_and_user_idp_registration(tenant_admin_details, admin_extra_details, tenant, db_name):
        """Create tenant and user and register on IDP."""

        set_db_for_router(db_name)
        UserRole.populate_default_user_roles(db_name)
        admin_role = UserRole.objects.filter(role_type=RoleTypeChoices.admin).first()
        tenant_admin = User.objects.create_superuser(**tenant_admin_details)
        tenant_admin.roles.add(admin_role)
        tenant_admin.password = make_password(settings.APP_SUPER_ADMIN["password"])
        tenant_admin.save()
        UserDetail.objects.create(**admin_extra_details, user=tenant_admin)
        PolicyCategory.populate_policies(db_name=db_name)
        auth_token = idp_admin_auth_token(raise_drf_error=True, field="name")
        success, data = idp_post_request(
            url_path=IDP_CONFIG["tenant_create_url"],
            auth_token=auth_token,
            data={
                "tenancyName": tenant.tenancy_name,
                "name": tenant.name,
                "adminEmailAddress": tenant_admin.email,
                "adminUserName": tenant_admin.email,
                "adminFirstName": tenant_admin.first_name,
                "adminSurname": tenant_admin.last_name,
                "isActive": True,
            },
        )
        if not success:
            raise serializers.ValidationError({"name": "IDP Registration failed."})
        tenant_idp_id = data["id"]
        success, data = idp_get_request(
            url_path=IDP_CONFIG["tenant_all_users_url"], auth_token=auth_token, params={"TenantId": tenant_idp_id}
        )
        if not success:
            raise serializers.ValidationError({"name": "IDP Registration failed."})
        user_idp_id = data["items"][0]["id"]

        success, admin_data = idp_post_request(
            url_path=IDP_CONFIG["external_reset_password_url"],
            auth_token=auth_token,
            data={
                "userName": tenant_admin.email,
                "tenantName": tenant.tenancy_name,
                "newPassword": settings.APP_SUPER_ADMIN["password"],
            },
        )
        if not success:
            raise serializers.ValidationError({"name": "IDP Admin Password set failed."})
        tenant_admin.idp_id = user_idp_id
        tenant_admin.save()
        set_db_for_router()
        tenant.idp_id = tenant_idp_id
        tenant.save()

    def to_representation(self, instance):
        """Tenant Retrieve Details as a JSON representation."""

        return TenantRetrieveModelSerializer(instance).data


class TenantUpdateModelSerializer(AppUpdateModelSerializer):
    """Update serializer class for `Tenant`."""

    tenant_configuration = TenantConfigurationModelSerializer(read_only=False)
    idp_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta(AppUpdateModelSerializer.Meta):
        model = Tenant
        fields = [
            "name",
            "idp_id",
            "logo",
            "issuer_url",
            "client_id",
            "sso_tenant_id",
            "secret_id",
            "secret_value",
            "allowed_login_domain",
            "is_domain_restricted_login",
            "tenant_configuration",
            "mml_id",
        ]

    def validate(self, attrs):
        """Validate logic for tenant update."""

        allowed_login_domain = attrs.get("allowed_login_domain")
        if attrs.get("is_domain_restricted_login") and not allowed_login_domain:
            raise serializers.ValidationError({"allowed_login_domain": "This field is required."})
        idp_id = attrs.pop("idp_id", None)
        if self.instance.is_keycloak and idp_id and not Tenant.objects.filter(idp_id=idp_id).exists():
            attrs["idp_id"] = idp_id
        return attrs

    def update(self, instance, validated_data):
        """Update tenant details."""

        tenant_configuration = validated_data.pop("tenant_configuration")
        tenant_config = instance.tenant_config
        TenantConfiguration.objects.filter(id=tenant_config.id).update(**tenant_configuration)
        return super().update(instance, validated_data)

    def get_meta_for_update(self, *args, **kwargs):
        """Overriden to add initial data of Tenant Configuration."""

        tenant_config = self.instance.tenant_config
        data = super().get_meta_for_update()
        data["initial"].update(
            {
                "tenant_configuration": TenantConfigurationModelSerializer(instance=tenant_config).get_meta_initial(),
                "is_keycloak": self.instance.is_keycloak,
            }
        )
        return data

    # This feature should not be given even at the FE level. IMPORTANT
    # def validate_tenancy_name(self, tenancy_name):
    #     """Validate name is already exists on IDP and locally."""
    #
    #     tenant = self.instance
    #     success, data = idp_post_request(
    #         url_path=IDP_CONFIG["tenant_availability_url"], data={"tenancyName": tenancy_name}
    #     )
    #     is_name_taken = Tenant.objects.filter(name=tenancy_name).exclude(id=tenant.id).exists()
    #
    #     if not success:
    #         raise serializers.ValidationError("IDP Connection Error")
    #
    #     tenant_id = data.get("tenantId")  # data.get("tenantId") will return id if idp tenant exists.
    #
    #     if tenant_id and (is_name_taken or tenant_id != tenant.idp_id):
    #         raise serializers.ValidationError(f"The Name {tenancy_name} is already taken.")
    #     return tenancy_name
