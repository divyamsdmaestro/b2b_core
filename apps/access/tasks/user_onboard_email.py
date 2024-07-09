from apps.access_control.config import RoleTypeChoices
from apps.common.helpers import get_tenant_website_url
from apps.mailcraft.config import MailTypeChoices, TemplateFieldChoices
from apps.mailcraft.tasks import BaseEmailTask


class UserOnboardEmailTask(BaseEmailTask):
    """Task to send email once user is onboarded."""

    def run(self, user_id, password, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User
        from apps.mailcraft.models import MailTemplate
        from apps.tenant_service.middlewares import get_current_sender_email

        self.switch_db(db_name)
        self.logger.info(f"Executing UserOnboardEmailTask for user_id: {user_id} on {db_name} database.")

        sender_email = get_current_sender_email()
        user = User.objects.get(id=user_id)
        mail_template = MailTemplate.objects.active().filter(type=MailTypeChoices.learner_welcome).first()
        email_context = {
            TemplateFieldChoices.user_name: user.name,
            TemplateFieldChoices.user_email: user.email,
            TemplateFieldChoices.website_url: get_tenant_website_url(db_name),
            TemplateFieldChoices.user_password: password,
            TemplateFieldChoices.user_role: RoleTypeChoices.labels.learner,
        }
        # Currently Only Learner role is supported.
        self.trigger_learner_mail(user, mail_template, email_context, sender_email)
        return True
