from django.core.files.storage import default_storage
from django.db import models
from django.template import Context, Template
from django.utils.html import strip_tags

from apps.common.helpers import get_tenant_website_url
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    CreationModel,
    NameModel,
)
from apps.common.tasks import SendEmailTask
from apps.learning.config import BaseUploadStatusChoices
from apps.mailcraft.config import MailTypeChoices, TemplateFieldChoices
from apps.mailcraft.models import MailTemplate
from apps.tenant_service.middlewares import get_current_sender_email


class Report(CreationModel, NameModel):
    """
    Report model for IIHT-B2B.

    Model Fields -
        PK          - id,
        FK          - created_by
        Fields      - uuid, status, file_url, data
        Datetime    - created_at, modified_at, start_date, end_date

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(CreationModel.Meta):
        default_related_name = "related_reports"

    # JSON Fields
    data = models.JSONField(default=dict)
    # Date Fields
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Url Fields
    file_url = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    # Choices
    status = models.CharField(choices=BaseUploadStatusChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    @classmethod
    def basic_data(cls, is_date_skipped=False):
        """Returns basic input data structure used to create Report."""

        return {
            "is_entire_learnings": True,
            "is_date_skipped": is_date_skipped,
            "is_master_report": True,
            "is_file_submission": False,
            "is_evaluated": False,
            "is_feedback_report": False,
            "course": [],
            "course_name": [],
            "learning_path": [],
            "learning_path_name": [],
            "advanced_learning_path": [],
            "advanced_learning_path_name": [],
            "user": [],
            "user_name": [],
            "user_group": [],
            "user_group_name": [],
            "is_send_email": False,
            "recipients": [],
        }

    def delete(self, using=None, keep_parents=False):
        """Overridden to remove the file from django default_storage."""

        file_path = self.file_url
        instance = super().delete()
        if file_path:
            default_storage.delete(file_path)
        return instance

    def call_report_emailtask(self, file_path, db_name=None):
        """function to call Report EmailTask"""

        mail_template = MailTemplate.objects.active().filter(type=MailTypeChoices.report_trigger).first()
        if not mail_template:
            return False
        url = get_tenant_website_url(db_name)
        email_context = {
            TemplateFieldChoices.user_name: self.created_by.name,
            TemplateFieldChoices.artifact_name: self.name,
            TemplateFieldChoices.completion_date: self.created_at,
            TemplateFieldChoices.website_url: url,
        }
        recipients = [self.created_by.email]
        if self.data["is_send_email"]:
            recipients += self.data["recipients"]
        sender_email = get_current_sender_email()
        template = Template(mail_template.content)
        html_body = template.render(Context(email_context))
        SendEmailTask().run_task(
            subject=mail_template.subject,
            message=strip_tags(html_body),
            recipients=recipients,
            sender_email=sender_email,
            html_message=html_body,
            attachments=[file_path],
            is_default_storage=True,
        )
        return True
