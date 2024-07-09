from .base import AppAPIView, NonAuthenticatedAPIMixin


class ServerStatusAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Just a ping-pong api view. Used to check if the server is up or not."""

    def get(self, *args, **kwargs):
        """Just send an empty response."""

        return self.send_response()
