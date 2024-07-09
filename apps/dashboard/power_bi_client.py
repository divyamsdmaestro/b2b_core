import json

from django.conf import settings
from requests import request


class PowerBIClient:
    """PowerBI REST API Client."""

    def __init__(self):
        self.login_email = settings.POWERBI_CONFIG["email"]
        self.login_password = settings.POWERBI_CONFIG["password"]
        self.login_url = settings.POWERBI_CONFIG["login_url"]
        self.client_id = settings.POWERBI_CONFIG["client_id"]
        self.client_secret = settings.POWERBI_CONFIG["client_secret"]

    @staticmethod
    def get_headers(auth_token=None):
        """Headers necessary for authorization."""

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        return headers

    def post(self, url_path, data, params=None, auth_token=None):
        """Make post request."""

        if params is None:
            params = {}

        response = request(method="POST", url=url_path, headers=self.get_headers(auth_token), data=data, params=params)
        try:
            response_data = response.json()
        except json.decoder.JSONDecodeError:
            response_data = None
        if response.status_code == 200:
            return True, response_data
        return False, response

    def ms_login(self):
        """Microsoft Login."""

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "resource": "https://analysis.windows.net/powerbi/api",
            "grant_type": "password",
            "username": self.login_email,
            "password": self.login_password,
        }
        return self.post(url_path=self.login_url, data=data)

    def get_report_embed_token(self, group_id, report_id, rls_data):
        """Generates embed token for the given report."""

        status, auth_token = self.ms_login()
        if not status:
            return False, auth_token
        access_token = auth_token["access_token"]
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
        url_path = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/GenerateToken"
        response = request(method="POST", url=url_path, headers=headers, json=rls_data)
        try:
            response_data = response.json()
        except json.decoder.JSONDecodeError:
            response_data = None
        if response.status_code == 200:
            return True, response_data
        return False, response
