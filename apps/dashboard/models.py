from django.db import models

from apps.access_control.config import RoleTypeChoices
from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, StatusModel
from apps.dashboard.config import PowerBIRoleChoices, RLSRoleChoices
from apps.dashboard.power_bi_client import PowerBIClient
from apps.tenant_service.middlewares import get_current_db_name, set_db_for_router
from config import settings


class PowerBIDetail(StatusModel):
    """
    Model to Store PowerBI Details.

    ********************* Model Fields *********************

        PK          - id,
        Fields      - access_role, report_id, report_name, embed_url, dataset_id,dataset_workspace_id, web_url, data
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none, active, inactive
    """

    class Meta(StatusModel.Meta):
        default_related_name = "related_power_bi_details"

    # Fields
    access_role = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=PowerBIRoleChoices.choices)
    report_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    report_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    embed_url = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    dataset_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    dataset_workspace_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    web_url = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    data = models.JSONField(default=dict)

    def __str__(self):
        """Report name as string rep."""

        return self.report_name

    @classmethod
    def get_dashboard_data(cls, user):
        """Return dashboard data for integrations based on role."""

        # TODO: Keycloak support need to be added if KC tenant is a default tenant.
        #  Currently IDP based tenant is a default tenant.

        from apps.dashboard.serializers import PowerBIDetailSerializer
        from apps.tenant_service.middlewares import get_current_tenant_details

        db = get_current_db_name()
        tenant_details = get_current_tenant_details()
        is_prolifics = tenant_details["id"] == 727  # prolifics tenant pk / id
        role_type = user.current_role.role_type
        role_name, rls_role, rls_custom_data = cls.get_rls_data(tenant_details, user, role_type, is_prolifics)
        set_db_for_router()
        instance = cls.objects.active().get_or_none(access_role=role_name)
        if not instance:
            raise ValueError("Unable to fetch data. Please contact support.")
        if instance.access_role in [
            PowerBIRoleChoices.tenant_user,
            PowerBIRoleChoices.tenant_manager,
            PowerBIRoleChoices.tenant_admin,
        ]:
            rls_username = settings.POWERBI_CONFIG["email"]
            rls_data = {
                "accessLevel": "View",
                "identities": [
                    {
                        "username": rls_username,
                        "customData": rls_custom_data,
                        "roles": [rls_role],
                        "datasets": [instance.dataset_id],
                    }
                ],
            }
        else:
            rls_data = {"accessLevel": "View"}
        data = PowerBIDetailSerializer(instance).data
        client = PowerBIClient()
        report_embed_status, report_embed_token = client.get_report_embed_token(
            group_id=instance.dataset_workspace_id, report_id=instance.report_id, rls_data=rls_data
        )
        if not report_embed_status:
            raise ValueError("Invalid workspace or report ID. Please contact support.")
        data["embed_token"] = report_embed_token
        set_db_for_router(db)
        return data

    @staticmethod
    def get_rls_data(tenant_details, user, role_type, is_prolifics):
        """Return PowerBI necessary parameters based on role_type."""

        match role_type:
            case RoleTypeChoices.admin:
                if tenant_details["idp_id"] == settings.IDP_B2B_TENANT_ID:
                    role_name = PowerBIRoleChoices.super_admin
                    rls_custom_data = None
                    rls_role = None
                else:
                    role_name = PowerBIRoleChoices.tenant_admin
                    rls_role = RLSRoleChoices.tenant_admin
                    if is_prolifics:
                        rls_custom_data = str(tenant_details["idp_id"])
                    else:
                        rls_custom_data = str(tenant_details["id"])
            case RoleTypeChoices.learner:
                role_name = PowerBIRoleChoices.tenant_user
                rls_role = RLSRoleChoices.tenant_user
                if is_prolifics:
                    rls_custom_data = str(user.idp_id)
                else:
                    rls_custom_data = str(user.id)
            case RoleTypeChoices.manager:
                role_name = PowerBIRoleChoices.tenant_manager
                rls_role = RLSRoleChoices.tenant_admin
                if is_prolifics:
                    rls_custom_data = str(tenant_details["idp_id"])
                else:
                    rls_custom_data = str(tenant_details["id"])
            case _:
                raise ValueError("Dashboard for Author role is not yet supported. Please contact support.")
        return role_name, rls_role, rls_custom_data

    @classmethod
    def get_report_builder_data(cls, user):
        """Return Report Builder data for integrations based on role."""

        # TODO: Keycloak support need to be added if KC tenant is a default tenant.
        #  Currently IDP based tenant is a default tenant.

        from apps.dashboard.serializers import PowerBIDetailSerializer
        from apps.tenant_service.middlewares import get_current_tenant_details

        db = get_current_db_name()
        tenant_details = get_current_tenant_details()
        is_prolifics = tenant_details["id"] == 727  # prolifics tenant pk / id
        role_type = user.current_role.role_type
        if role_type != RoleTypeChoices.admin:
            raise ValueError("User is not an admin to access this API.")
        set_db_for_router()
        instance = cls.objects.active().get_or_none(access_role=PowerBIRoleChoices.super_admin)
        if not instance:
            raise ValueError("Unable to fetch data. Please contact support.")
        rls_username = settings.POWERBI_CONFIG["email"]
        if is_prolifics:
            custom_data = tenant_details["idp_id"]
        else:
            custom_data = tenant_details["id"]
        rls_data = {
            "accessLevel": "View",
            "identities": [
                {
                    "username": rls_username,
                    "customData": custom_data,
                    "roles": [RLSRoleChoices.tenant_admin_rb],
                    "datasets": [instance.dataset_id],
                }
            ],
        }
        data = PowerBIDetailSerializer(instance).data
        client = PowerBIClient()
        report_embed_status, report_embed_token = client.get_report_embed_token(
            group_id=instance.dataset_workspace_id, report_id=instance.report_id, rls_data=rls_data
        )
        if not report_embed_status:
            raise ValueError("Invalid workspace or report ID. Please contact support.")
        data["embed_token"] = report_embed_token
        set_db_for_router(db)
        return data
