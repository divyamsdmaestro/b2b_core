from django.template import Context, Template
from django.utils.html import strip_tags

from apps.access_control.config import RoleTypeChoices
from apps.common.tasks import BaseAppTask, SendEmailTask


class BaseEmailTask(BaseAppTask):
    """Base Class for sending emails."""

    @staticmethod
    def trigger_learner_mail(user, mail_template, context, sender_email):
        """Just a DRY method to trigger email notifications."""

        if not mail_template or RoleTypeChoices.learner not in user.roles.values_list("role_type", flat=True):
            return False, "Mail template not found Or User is not a learner."

        template = Template(mail_template.content)
        html_body = template.render(Context(context))
        SendEmailTask().run_task(
            subject=mail_template.subject,
            message=strip_tags(html_body),
            recipients=user.email,
            html_message=html_body,
            sender_email=sender_email,
        )
