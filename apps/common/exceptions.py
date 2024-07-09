from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ObjectExpired(APIException):
    """
    Custom exception to state that an object has expired. Ideally
    it's a 404, but instead of telling the user that. We tell
    them that it has expired. In a subtle way.
    """

    status_code = status.HTTP_410_GONE
    default_detail = _("The requested URL has expired.")
    default_code = "url_expired"


class InvalidToken(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"message": "Invalid Token."}
    default_code = "invalid_token"


class InvalidUser(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {"message": "User Not Found."}
    default_code = "invalid_user"


class InactiveUser(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {"message": "User Account is not Active."}
    default_code = "inactive_user"


class InactiveTenant(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {"message": "Tenant is not Active."}
    default_code = "inactive_tenant"


class InvalidIssuerURL(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"message": "Issuer URL Not Found."}
    default_code = "inactive_issuer_url"


class IDPAuthFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"message": "IDP Authentication Failed."}
    default_code = "idp_auth_failed"


class KCAuthFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"message": "KeyCloak Authentication Failed."}
    default_code = "kc_auth_failed"
