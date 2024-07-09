from datetime import timedelta

from django.utils import timezone

from config.celery_app import app as celery_app


@celery_app.task
def handle_enrollment_reminder_mail():
    """Cron job to trigger mail for the enrollment reminder."""

    print("Enrollment Reminder Mail Task - working")
    from apps.common.helpers import batch, get_tenant_website_url
    from apps.learning.config import BaseUploadStatusChoices
    from apps.mailcraft.config import MailTypeChoices
    from apps.mailcraft.models import MailTemplate
    from apps.my_learning.models import Enrollment, EnrollmentReminder
    from apps.tenant_service.middlewares import get_current_sender_email, set_db_for_router
    from apps.tenant_service.models import DatabaseRouter

    current_date = timezone.now()
    set_db_for_router()
    for router in DatabaseRouter.objects.filter(setup_status=BaseUploadStatusChoices.completed):
        print(f"\n** Getting Enrollment Objects for {router.database_name}. **")
        router.add_db_connection()
        set_db_for_router(router.database_name)
        mail_template = MailTemplate.objects.active().filter(type=MailTypeChoices.enrollment_expiration).first()
        if not mail_template:
            continue
        reminders = EnrollmentReminder.objects.all()
        kwargs = {
            "url": get_tenant_website_url(router.database_name),
            "sender_email": get_current_sender_email(),
            "mail_template": mail_template,
        }
        for reminder in reminders:
            enrolled_date = current_date.date() - timedelta(days=reminder.days)
            for enrollment in batch(
                Enrollment.objects.filter(
                    learning_type=reminder.learning_type,
                    action_date=enrolled_date,
                    end_date__gte=current_date,
                    user__isnull=False,
                    user_group__isnull=True,
                    is_enrolled=True,
                )
            ):
                enrollment.trigger_enrollment_reminder_email(enrollment.user, **kwargs)
            for enrollment in Enrollment.objects.filter(
                learning_type=reminder.learning_type,
                action_date=enrolled_date,
                end_date__gte=current_date,
                user_group__isnull=False,
                user__isnull=True,
                is_enrolled=True,
            ):
                for user in batch(enrollment.user_group.members.all()):
                    enrollment.trigger_enrollment_reminder_email(user, **kwargs)
        set_db_for_router()
    return True
