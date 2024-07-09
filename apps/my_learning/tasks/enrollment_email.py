from apps.common.helpers import get_tenant_website_url
from apps.mailcraft.config import MailTypeChoices, TemplateFieldChoices
from apps.mailcraft.tasks import BaseEmailTask
from apps.my_learning.config import ApprovalTypeChoices, EnrollmentTypeChoices


class UserEnrollmentEmailTask(BaseEmailTask):
    """Task to send email based on enrollment."""

    def run(self, enrollment_id, db_name, user_id=None, user_group_id=None, **kwargs):
        """Run handler."""

        from apps.my_learning.models import Enrollment
        from apps.tenant_service.middlewares import get_current_sender_email

        self.switch_db(db_name)
        self.logger.info(f"Executing UserEnrollmentEmailTask on {db_name} database.")

        sender_email = get_current_sender_email()
        enrollment: Enrollment = Enrollment.objects.get(id=enrollment_id)
        if not enrollment.is_enrolled:
            return False, "Not enrolled yet."
        item_name, mail_template_type = self.get_artifact_and_template_type(enrollment)
        if not item_name or not mail_template_type:
            return False, f"Not supported learning type {enrollment.learning_type} for sending email."
        url = get_tenant_website_url(db_name)
        self.send_enrollment_mail(
            item_name, mail_template_type, url, user_id=user_id, group_id=user_group_id, sender_email=sender_email
        )
        return True

    @staticmethod
    def get_artifact_and_template_type(enrollment):
        """Return the learning model's name and template type."""

        match enrollment.learning_type:
            case EnrollmentTypeChoices.course:
                item_name = enrollment.course.name
                if enrollment.approval_type in [ApprovalTypeChoices.tenant_admin, ApprovalTypeChoices.super_admin]:
                    mail_template_type = MailTypeChoices.course_admin_assign
                else:
                    mail_template_type = MailTypeChoices.course_self_enrollment
            case EnrollmentTypeChoices.learning_path:
                item_name = enrollment.learning_path.name
                if enrollment.approval_type in [ApprovalTypeChoices.tenant_admin, ApprovalTypeChoices.super_admin]:
                    mail_template_type = MailTypeChoices.lp_admin_assign
                else:
                    mail_template_type = MailTypeChoices.lp_self_enrollment
            case EnrollmentTypeChoices.advanced_learning_path:
                item_name = enrollment.advanced_learning_path.name
                if enrollment.approval_type in [ApprovalTypeChoices.tenant_admin, ApprovalTypeChoices.super_admin]:
                    mail_template_type = MailTypeChoices.alp_admin_assign
                else:
                    mail_template_type = MailTypeChoices.alp_self_enrollment
            case _:
                item_name, mail_template_type = None, None
        return item_name, mail_template_type

    def send_enrollment_mail(self, item_name, mail_template_type, url, sender_email, user_id=None, group_id=None):
        """Send Learning Path enrollment email."""

        from apps.access.models import User
        from apps.access_control.models import UserGroup
        from apps.mailcraft.models import MailTemplate

        mail_template = MailTemplate.objects.active().filter(type=mail_template_type).first()
        email_context = {
            TemplateFieldChoices.website_url: url,
            TemplateFieldChoices.artifact_name: item_name,
        }
        if group_id:
            group = UserGroup.objects.get(id=group_id)
            for user in group.members.all():
                self.send_mail_to_user(email_context, user, mail_template, sender_email)
        else:
            user = User.objects.get(id=user_id)
            self.send_mail_to_user(email_context, user, mail_template, sender_email)

    def send_mail_to_user(self, email_context, user, mail_template, sender_email):
        """Just a DRY function."""

        email_context[TemplateFieldChoices.user_name] = user.name
        self.trigger_learner_mail(user, mail_template, email_context, sender_email)
