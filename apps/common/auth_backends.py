import json

import jwt
import requests
from django.contrib.auth.models import AnonymousUser
from jwt import PyJWKClient
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied

from apps.common.communicator import get_request
from apps.common.exceptions import (
    IDPAuthFailed,
    InactiveTenant,
    InactiveUser,
    InvalidIssuerURL,
    InvalidUser,
    KCAuthFailed,
)
from config import settings
from config.settings.base import IDP_CONFIG


class CustomAppAuthentication(BaseAuthentication):
    """Custom authentication method to handle IDP4 & KeyCloak authentication."""

    def authenticate(self, request):
        """Function that authenticates the token type, Refers from django's default authentication classes."""

        from apps.tenant_service.middlewares import set_db_for_router

        # self.validate_user_agent(request) # Note: Commented. As per @Dakshan's context on 22-05-24.
        set_db_for_router()
        tenant_id, kc_token = request.headers.get("tenant-id", None), request.headers.get("kc-token", None)
        idp_token, sso_token = request.headers.get("idp-token", None), request.headers.get("sso-token", None)
        if idp_token:
            tenant, user = self.authenticate_idp_token(idp_token)
        elif tenant_id and sso_token:
            tenant, user = self.authenticate_sso_token(tenant_id, sso_token)
        elif tenant_id and kc_token:
            tenant, user = self.validate_keycloak_token(tenant_id, kc_token)
        else:
            tenant, user = None, None
        if tenant and user and not user.is_anonymous:
            tenant, user = self.validate_tenant_domain_login_restrictions(tenant, user)
        return user or AnonymousUser(), None

    @staticmethod
    def validate_user_agent(request):
        """Validate the user agent of the request received from client."""

        user_agent = request.headers.get("User-Agent") or "/"
        host = request.headers.get("Host")
        if user_agent.split("/")[0] in ["PostmanRuntime"] and (
            "techademyb2b.site" in host or "techademyb2.com" in host
        ):
            raise PermissionDenied()
        return True

    @staticmethod
    def validate_tenant_domain_login_restrictions(tenant, user):
        """Tenant domain level login restrictions validation."""

        if tenant.is_domain_restricted_login:
            user_email = f"{user.email}".lower()
            _, mail_provider = user_email.split("@")
            if mail_provider not in ["iiht.com", "techademy.com"] and mail_provider != tenant.allowed_login_domain:
                return tenant, AnonymousUser()
        return tenant, user

    def authenticate_idp_token(self, idp_token):
        """validate the idp-token & user."""

        success, data = get_request(
            service="IDP",
            url_path=IDP_CONFIG["get_current_login_informations"],
            auth_token=idp_token,
        )
        if success and data.get("user"):
            tenant = self.get_tenant_or_404(data["user"]["tenantId"])
            user = self.get_user_account(data["user"]["id"], tenant=tenant)
            return tenant, user
        raise IDPAuthFailed()

    def authenticate_sso_token(self, tenant_id, token):
        """Validate the sso token & user."""

        tenant = self.get_tenant_or_404(tenant_id)
        issuer = tenant.issuer_url
        if not issuer:
            raise InvalidIssuerURL()
        success, data = get_request(
            service=None,
            host=issuer,
            url_path=IDP_CONFIG["get_current_login_informations"],
            auth_token=token,
        )
        if success and data.get("user"):
            user = self.get_user_account(data["user"]["id"], tenant=tenant)
            return tenant, user
        return None, None

    def validate_keycloak_token(self, tenant_id, token):
        """Validate KC token."""

        tenant = self.get_tenant_or_404(tenant_id, is_kc=True)
        issuer = tenant.issuer_url
        if not issuer:
            raise InvalidIssuerURL()

        # jwt verification options
        options = {
            "verify_signature": True,
            "require": ["exp", "iss"],
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": False,
        }
        # Verify the JWT token
        try:
            import ssl

            jwks_endpoint = self.get_jwks_uri(issuer)
            # import urllib.request
            # For now disabling SSL certificate verification for testing
            """TO-DO-Need to get ssl certificate path here"""
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            jwks_client = PyJWKClient(uri=jwks_endpoint, cache_keys=True, lifespan=1200, ssl_context=ssl_context)
            jwk_set = jwks_client.get_jwk_set()
            jwk_key = jwk_set.keys[0]
            decoded_token = jwt.decode(
                jwt=token, key=jwk_key.key, algorithms=["RS256"], options=options, issuer=issuer
            )
            user = self.get_user_account(decoded_token["email"], tenant=tenant, is_kc=True)
            return tenant, user
        except Exception:
            pass
        raise KCAuthFailed()

    @staticmethod
    def get_jwks_uri(issuer):
        openid_config_url = f"{issuer}/.well-known/openid-configuration"
        response = requests.get(openid_config_url, verify=False)
        data = json.loads(response.content)
        return data.get("jwks_uri")

    @staticmethod
    def get_tenant_or_404(tenant_id=None, is_kc=False):
        """Return Tenant Instance or 404."""

        from rest_framework.generics import get_object_or_404

        from apps.tenant.models import Tenant

        if not tenant_id and not is_kc:  # In IDP Default Tenant Users are not getting tenant info so just a hack.
            return Tenant.objects.get(idp_id=settings.IDP_B2B_TENANT_ID)

        if is_kc:
            tenant = get_object_or_404(Tenant, uuid=tenant_id)
        else:
            tenant = get_object_or_404(Tenant, idp_id=tenant_id)
        if not tenant.is_active:
            raise InactiveTenant()
        return tenant

    @staticmethod
    def get_user_account(user_id, tenant, is_kc=False):
        """Return Tenant Instance or Anonymous obj."""

        # TODO: FOR KC NEED TO HANDLE SAME EMAIL PRESENT IN 2 TENANTS

        from apps.access.models import User
        from apps.tenant_service.middlewares import set_db_for_router

        if tenant.idp_id == settings.IDP_B2B_TENANT_ID:
            set_db_for_router()
        else:
            tenant.db_router.add_db_connection()
            set_db_for_router(tenant.db_name)

        if is_kc:
            user = User.objects.filter(email=user_id).first()
        else:
            user = User.objects.filter(idp_id=user_id).first()
        if not user:
            raise InvalidUser()
        if not user.is_active:
            raise InactiveUser()
        return user
