import logging

from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404

from apps.access.serializers.v1 import UserReadOnlyModelSerializer
from apps.common.helpers import get_image_field_url
from apps.common.idp_service import idp_post_request
from apps.common.views.api import AppAPIView
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.leaderboard.config import MilestoneChoices
from apps.leaderboard.tasks import CommonLeaderboardTask
from apps.tenant.models import TenantDomain
from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_details, set_db_for_router
from config import settings
from config.settings import IDP_CONFIG

logger = logging.getLogger(__name__)


def logged_in_response_data_1(user):
    """Central data for refresh and login for FE centralization."""

    return {
        "token": Token.objects.get(user=user).key,
        "user": {
            "username": user.username,
            "email": user.email,
        },
    }


class RefreshAuthTokenAPIView(AppAPIView):
    """Refresh APIView for the FE to authenticate tokens."""

    def get(self, *args, **kwargs):
        return self.send_response(
            data=logged_in_response_data_1(self.get_user()),
        )


class TenantInitialDataAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Send basic details of the user & tenant based on logged in user token."""

    # TODO: Move this API inside tenant app.

    def get(self, request):
        """Returns the banner image and logo image for the given tenant domain."""

        set_db_for_router()
        domain = request.headers.get("domain", None)
        if not domain:
            domain = settings.APP_DEFAULT_TENANT_DOMAIN
        domain_instance = get_object_or_404(TenantDomain, name=domain, is_active=True)
        tenant = domain_instance.tenant
        data = {
            "banner_image_url": None,
            "logo_image_url": get_image_field_url(tenant, field="logo"),
            "contact_number": str(tenant.contact_number),
            "footer_email": None,
            "tenancy_name": tenant.tenancy_name,
            "issuer_url": tenant.issuer_url,
            "client_id": tenant.client_id,
            "sso_tenant_id": tenant.sso_tenant_id,
            "secret_id": tenant.secret_id,
            "secret_value": tenant.secret_value,
            "is_keycloak": tenant.is_keycloak,
        }
        if config_model := tenant.related_tenant_configurations.first():
            data.update(
                {
                    "banner_image_url": get_image_field_url(config_model, field="banner_image"),
                    "footer_email": config_model.footer_email,
                }
            )
        return self.send_response(data=data)


class CurrentSessionInfoAPIView(AppAPIView):
    """Send basic details of the user & tenant based on logged in user token."""

    def get(self, request, *args, **kwargs):
        """Handle on post."""

        # TODO From the feature flags, Pass restricted features to frontend as a list

        user = self.get_user()
        user_details = {"b2b_info": UserReadOnlyModelSerializer(user).data}
        user_details["b2b_info"]["is_admin"] = user.is_staff
        user_details["b2b_info"]["active_role_type"] = user.get_active_role(is_reset=True)
        user_details["b2b_info"]["is_tc_agreed"] = user.data.get("is_tc_agreed", False)
        user_details["b2b_info"]["is_area_of_interest_given"] = user.data.get("is_area_of_interest_given")
        user_details["tenant_info"] = get_current_tenant_details()
        user_details["cert_access_key"] = settings.CERT_ACCESS_KEY
        user_details["ccms_access_key"] = settings.CCMS_CONFIG[
            "access_token"
        ]  # TODO: Need to add restriction to send this key
        CommonLeaderboardTask().run_task(
            milestone_names=MilestoneChoices.first_login, user_id=user.id, db_name=get_current_db_name()
        )
        return self.send_response(data=user_details)


class LogoutAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Invalidate a token and logout user."""

    def post(self, request, *args, **kwargs):
        """Handle on post."""

        user = self.get_authenticated_user()
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        user_idp_token = user.data.get("idp_token")
        if idp_token != user_idp_token:
            if idp_token:
                idp_post_request(url_path=IDP_CONFIG["logout_url"], auth_token=idp_token)
            if user_idp_token:
                idp_post_request(url_path=IDP_CONFIG["logout_url"], auth_token=user_idp_token)
        else:
            idp_post_request(url_path=IDP_CONFIG["logout_url"], auth_token=user_idp_token)

        if user:
            Token.objects.filter(user=user).delete()

        return self.send_response()
