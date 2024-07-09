from apps.common.base_communicator import BaseCommunicator
from config.settings import CHAT_ACCESS_KEY, CHAT_CONFIG


class ChatCommunicator(BaseCommunicator):
    """Communicates with Chat microservice and returns the response."""

    @staticmethod
    def get_host():
        """Return host of chat microservice."""

        return CHAT_CONFIG["host"]

    @staticmethod
    def get_headers(token=None, idp_token=None, host=None, headers={}):
        """Headers necessary for authorization."""

        headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"CHAT_ACCESS_KEY {CHAT_ACCESS_KEY}",
            }
        )
        return headers


def chat_post_request(url_path, data, headers=None):
    """Helper function to call chat communicator post request."""

    return ChatCommunicator().post(url_path=url_path, data=data, headers=headers)
