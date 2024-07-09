from django.core.management.base import BaseCommand


class AppBaseCommand(BaseCommand):
    """Base class for all Management commands. Just includes some DRY stuff."""

    def print_styled_message(self, message: str, style_type: str = "HTTP_SERVER_ERROR"):
        """Prints the message along with style in the console."""

        style_func = getattr(self.style, style_type, self.style.HTTP_SERVER_ERROR)
        self.stdout.write(style_func(message))
