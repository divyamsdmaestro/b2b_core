from apps.common.base_communicator import BaseCommunicator
from config.settings import CERT_CONFIG


class CertificateCommunicator(BaseCommunicator):
    """
    Communicates with certificate micro services and returns the response.
    This is the one way class to communicate with the
    running certificate micro services.
    """

    @staticmethod
    def get_host():
        """Return host of certificate micro services."""

        return CERT_CONFIG["host"]

    @staticmethod
    def get_headers(token=None, idp_token=None, host=None, headers=None):
        """Headers necessary for authorization."""

        headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"CERT_ACCESS_KEY {token}"

        return headers
