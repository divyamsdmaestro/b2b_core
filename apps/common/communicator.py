from django.conf import settings
from rest_framework.authentication import get_authorization_header

from apps.common.helpers import make_http_request
from apps.tenant_service.middlewares import get_current_tenant_details


class Communicator:
    """
    Communicates with microservices and returns the response. This is the one way class to communicate with the
    running microservice.

    """

    @staticmethod
    def get_host(service=None, host=None):
        """Returns service host."""

        tenant_details = get_current_tenant_details()
        if service == "IDP":
            service_host = settings.IDP_CONFIG["host"]
        elif service == "YAKSHA":
            service_host = tenant_details.get("yaksha_host", None) or settings.YAKSHA_CONFIG["host"]
        elif service == "VIRTUTOR":
            service_host = tenant_details.get("virtutor_host", None) or settings.VIRTUTOR_CONFIG["host"]
        elif service == "CCMS":
            service_host = settings.CCMS_CONFIG["host"]
        elif service == "WECP":
            service_host = settings.WECP_CONFIG["host"]
        elif service == "YAKSHA_ONE":
            service_host = settings.YAKSHA_CONFIG["one_host"]
        else:
            service_host = host

        return service_host

    @staticmethod
    def get_headers(auth_token, service="IDP", headers=None):
        """Headers necessary for authorization."""

        headers["Content-Type"] = "application/json"

        if service in ["IDP", "VIRTUTOR", "YAKSHA"]:
            headers["Authorization"] = f"Bearer {auth_token}"
        elif service == "CCMS":
            headers["Authorization"] = f"CcmsAccessKey {settings.CCMS_CONFIG['access_token']}"
        elif service == "WECP":
            headers["x-api-key"] = auth_token
        else:
            headers["Authorization"] = f"Bearer {auth_token}"

        return headers

    def get(self, service, url_path, host=None, auth_token=None, params=None, headers=None):
        """Make get request."""

        if params is None:
            params = {}

        return make_http_request(
            url=f"{self.get_host(service, host)}{url_path}",
            method="GET",
            params=params,
            headers=self.get_headers(auth_token=auth_token, service=service, headers=headers or {}),
        )

    def post(self, service, url_path, host=None, data=None, auth_token=None, params=None, headers=None):
        """Make post request."""

        if data is None:
            data = {}
        if params is None:
            params = {}
        return make_http_request(
            url=f"{self.get_host(service, host)}{url_path}",
            method="POST",
            data=data,
            params=params,
            headers=self.get_headers(auth_token, service=service, headers=headers or {}),
        )

    def put(self, service, url_path, host=None, data=None, auth_token=None, params=None, headers=None):
        """Make post request."""

        if data is None:
            data = {}
        if params is None:
            params = {}

        return make_http_request(
            url=f"{self.get_host(service, host)}{url_path}",
            method="PUT",
            data=data,
            params=params,
            headers=self.get_headers(auth_token, service=service, headers=headers or {}),
        )


def post_request(service, url_path, host=None, data=None, auth_token=None, params=None):
    """Makes post request."""

    response = Communicator().post(
        service=service, host=host, url_path=url_path, data=data, auth_token=auth_token, params=params
    )
    if response.get("status_code") == 200:
        return True, response["data"]
    return False, response


def put_request(service, url_path, host=None, data=None, auth_token=None, params=None, headers=None):
    """Makes post request."""

    response = Communicator().put(
        service=service, host=host, url_path=url_path, data=data, auth_token=auth_token, params=params, headers=headers
    )
    if response.get("status_code") == 200:
        return True, response["data"]
    return False, response


def get_request(service, url_path, host=None, auth_token=None, params=None, headers=None):
    """Makes get request."""

    response = Communicator().get(
        service=service, host=host, url_path=url_path, auth_token=auth_token, params=params, headers=headers
    )
    if response.get("status_code") == 200:
        return True, response["data"]
    return False, response["data"]


def get_auth_token(request):
    """Returns the auth token passed in header."""

    auth = get_authorization_header(request).split()

    return None if not auth or len(auth) != 2 else auth[1].decode()
