from django.conf import settings

from apps.common.mail import app_send_mail
from apps.common.tasks.base import BaseOutboundAppTask


class SendEmailTask(BaseOutboundAppTask):
    """Task to send email in the background."""

    perform_run_task = settings.APP_SWITCHES["SEND_EMAILS"]
    outbound_log_category = "outbound__email"

    def run(self, subject, message, recipients, html_message, sender_email, *args, **kwargs):
        if not isinstance(recipients, list):
            recipients = [recipients]
        app_send_mail(
            subject=subject,
            message=message,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
            from_email=sender_email,
            reply_to=[],
            **kwargs,
        )
