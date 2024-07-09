from django.conf import settings
from rest_framework import serializers
from rest_framework.authentication import get_authorization_header

from apps.common.base_communicator import BaseCommunicator
from config.settings import IDP_CONFIG


class IDPCommunicator(BaseCommunicator):
    """
    Communicates with IDP services and returns the response. This is the one way class to communicate with the
    running IDP service.

    IDP communicates using only two methods => `GET` & `POST`.
    """

    @staticmethod
    def get_host():
        """Returns IDP host."""

        return settings.IDP_CONFIG["host"]

    @staticmethod
    def get_headers(token, idp_token, headers=None, host=None):
        """Headers necessary for authorization."""

        headers = {"Content-Type": "application/json"}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers


def idp_post_request(url_path, data=None, auth_token=None, params=None):
    """Makes an IDP post request."""

    response = IDPCommunicator().post(url_path=url_path, data=data, token=auth_token)
    if response.get("status_code") == 200:
        return True, response["data"]
    return False, response


def idp_get_request(url_path, auth_token=None, params=None):
    """Makes an IDP post request."""

    response = IDPCommunicator().get(url_path=url_path, token=auth_token, params=params)
    if response.get("status_code") == 200:
        return True, response["data"]
    return False, response


def idp_admin_auth_token(raise_drf_error=True, field=None):
    """Returns the IDP admin auth token."""

    success, data = idp_post_request(
        url_path=IDP_CONFIG["authenticate_url"],
        data={
            "userNameOrEmailAddress": settings.IDP_ADMIN_EMAIL,
            "password": settings.IDP_ADMIN_PASSWORD,
            "rememberClient": True,
            # "tenancyName": settings.IDP_ADMIN_TENANCY_NAME,  # For Super Admin it's not required.
        },
    )
    if not success and raise_drf_error:
        assert field
        raise serializers.ValidationError({field: "IDP Authentication failed!"})
    return data["accessToken"]


def get_auth_token(request):
    """Returns the auth token passed in header."""

    auth = get_authorization_header(request).split()

    return None if not auth or len(auth) != 2 else auth[1].decode()
