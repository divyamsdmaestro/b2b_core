from apps.mailcraft.tasks.common import BaseEmailTask


class BaseLearningEmailTask(BaseEmailTask):
    """Base Class for sending learnings related emails."""

    def send_learning_email(self, artifact_name, user, db_name, completion_date, mail_types):
        """Just a DRY method to trigger learner email function."""

        from apps.common.helpers import get_tenant_website_url
        from apps.mailcraft.config import MailTypeChoices, TemplateFieldChoices
        from apps.mailcraft.models import MailTemplate
        from apps.tenant_service.middlewares import get_current_sender_email

        self.logger.info(f"Got Email Task For : {mail_types} on {db_name}.")

        sender_mail = get_current_sender_email()
        mail_templates = MailTemplate.objects.active()
        email_context = {
            TemplateFieldChoices.user_name: user.name,
            TemplateFieldChoices.artifact_name: artifact_name,
            TemplateFieldChoices.completion_date: completion_date,
            TemplateFieldChoices.website_url: get_tenant_website_url(db_name),
        }
        for mail_type in mail_types:
            if mail_template := mail_templates.filter(type=mail_type).first():
                self.trigger_learner_mail(user, mail_template, email_context, sender_mail)
                mail_label = MailTypeChoices.get_choice(mail_type).label
                self.logger.info(f"{mail_label} email sent to learner.")
        return True
