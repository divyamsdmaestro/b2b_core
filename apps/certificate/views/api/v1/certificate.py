from rest_framework.response import Response

from apps.certificate.communicator import CertificateCommunicator
from apps.common.helpers import process_request_headers
from apps.common.views.api import AppAPIView
from apps.tenant_service.middlewares import get_current_tenant_idp_id
from config.settings import CERT_ACCESS_KEY


class CertificateAPIView(AppAPIView):
    """API View for certificate CRUD."""

    def get_url_path(self):
        """Returns the URL path of the current HTTP request."""

        return self.request.path

    def get(self, request, *args, **kwargs):
        """Overridden to make GET request to certificate microservices to retrieve and list the certificate."""

        url_path = self.get_url_path()
        headers = process_request_headers({"headers": dict(request.headers)})
        response = CertificateCommunicator().get(
            url_path=url_path,
            token=CERT_ACCESS_KEY,
            params={"tenant_id": get_current_tenant_idp_id()},
            headers=headers,
        )
        return Response(response["data"], status=response.get("status_code"))

    def post(self, request, *args, **kwargs):
        """Overridden to make POST request to certificate microservices to create a certificate."""

        url_path = self.get_url_path()
        files = request.FILES
        data = None if files else request.data
        headers = process_request_headers({"headers": dict(request.headers)})
        response = CertificateCommunicator().post(
            url_path=url_path, token=CERT_ACCESS_KEY, data=data, headers=headers, files=files
        )
        return Response(response["data"], status=response.get("status_code"))

    def put(self, request, *args, **kwargs):
        """Overridden to make PUT request to certificate microservices to update the certificate."""

        url_path = self.get_url_path()
        data = request.data
        headers = process_request_headers({"headers": dict(request.headers)})
        response = CertificateCommunicator().put(url_path=url_path, token=CERT_ACCESS_KEY, data=data, headers=headers)
        return Response(response["data"], status=response.get("status_code"))

    def delete(self, request, *args, **kwargs):
        """
        Overridden to make DELETE request to certificate microservices and
        soft-delete the certificate by updating `is_deleted` and `is_active`
        fields to True and False respectively.
        """

        url_path = self.get_url_path()
        headers = process_request_headers({"headers": dict(request.headers)})
        response = CertificateCommunicator().delete(url_path=url_path, token=CERT_ACCESS_KEY, headers=headers)
        return Response(response["data"], status=response.get("status_code"))
