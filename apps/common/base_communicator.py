from apps.common.helpers import make_http_request


class BaseCommunicator:
    """
    Base class for communicators used to send HTTP requests to microservices.
    Specific communicators should inherit from this class and implement the details
    of communication with their respective microservices.
    """

    @staticmethod
    def get_host():
        """Returns host."""

        pass

    @staticmethod
    def get_headers(token, idp_token, host=None, headers=None):
        """Headers necessary for authorization."""

        pass

    def get(self, url_path, token=None, params=None, idp_token=None, host=None, headers=None):
        """Make get request."""

        if params is None:
            params = {}

        return make_http_request(
            url=f"{self.get_host()}{url_path}",
            method="GET",
            params=params,
            headers=self.get_headers(token=token, idp_token=idp_token, headers=headers, host=host),
        )

    def post(self, url_path, data=None, token=None, params=None, idp_token=None, files=None, host=None, headers=None):
        """Make post request."""

        headers = self.get_headers(token=token, idp_token=idp_token, headers=headers, host=host)
        if data is None:
            data = {}
        if params is None:
            params = {}
        if files:
            headers.pop("Content-Type", None)
        return make_http_request(
            url=f"{self.get_host()}{url_path}",
            method="POST",
            data=data,
            files=files,
            params=params,
            headers=headers,
        )

    def put(self, url_path, data=None, token=None, params=None, idp_token=None, headers=None, host=None):
        """Make put request."""

        headers = self.get_headers(token=token, idp_token=idp_token, headers=headers, host=host)
        if data is None:
            data = {}
        if params is None:
            params = {}
        if not host:
            host = self.get_host()

        return make_http_request(
            url=f"{host}{url_path}",
            method="PUT",
            data=data,
            params=params,
            headers=headers,
        )

    def delete(self, url_path, data=None, token=None, params=None, idp_token=None, headers=None, host=None):
        """Make delete request."""

        headers = self.get_headers(token=token, idp_token=idp_token, headers=headers, host=host)
        if params is None:
            params = {}
        if not host:
            host = self.get_host()

        return make_http_request(
            url=f"{host}{url_path}",
            method="DELETE",
            data=data,
            params=params,
            headers=headers,
        )
