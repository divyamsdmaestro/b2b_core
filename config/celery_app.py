import os

from celery import Celery
from celery.schedules import crontab
from django.utils.module_loading import import_string

from config import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("apps")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Register class based tasks are not auto registered by default.
# Ref: https://github.com/celery/celery/issues/5992#issuecomment-781857785
for _import_string in [
    "apps.common.tasks.SendEmailTask",
    "apps.leaderboard.tasks.CommonLeaderboardTask",
    "apps.learning.tasks.ResourceUploadTask",
    "apps.learning.tasks.UpdateCatalogueLearningDataTask",
    "apps.learning.tasks.CourseBulkUploadTask",
    "apps.my_learning.tasks.UserBulkEnrollTask",
    "apps.my_learning.tasks.PlaygroundTrackingTask",
    "apps.my_learning.tasks.PlaygroundGroupEnrollmentTask",
    "apps.my_learning.tasks.PlaygroundGroupTrackingTask",
    "apps.my_learning.tasks.CourseProgressUpdateTask",
    "apps.my_learning.tasks.LPProgressUpdateTask",
    "apps.my_learning.tasks.ALPProgressUpdateTask",
    "apps.virtutor.tasks.SessionParticipantUpdateTask",
    "apps.learning.tasks.ScormUploadTask",
    "apps.access.tasks.UserOnboardEmailTask",
    "apps.my_learning.tasks.UserEnrollmentEmailTask",
    "apps.my_learning.tasks.CalendarActivityCreationTask",
    "apps.access.tasks.UserBulkUploadTask",
    "apps.access.tasks.AutoAssignLearningTask",
    "apps.my_learning.tasks.EnrollmentBulkUploadTask",
    "apps.my_learning.tasks.BulkUnenrollmentTask",
    "apps.my_learning.tasks.ReportGenerationTask",
    "apps.my_learning.tasks.FileSubmissionReportGenerationTask",
    "apps.my_learning.tasks.LeaderboardReportGenerationTask",
    "apps.my_learning.tasks.FeedbackReportGenerationTask",
    "apps.my_learning.tasks.SkillOntologyProgressUpdateTask",
    "apps.techademy_one.v1.tasks.T1TenantSetupTask",
    "apps.techademy_one.v1.tasks.T1BulkUserOnboardTask",
    "apps.leaderboard.tasks.badges.CommonBadgeTask",
    "apps.learning.tasks.LearningCloneTask",
    "apps.tenant.tasks.MasterReportTableTask",
]:
    app.register_task(import_string(_import_string)())


def is_beat_debug():
    """
    Returns if the celery beat is running on debug mode. Debug mode is used for
    development purposes on the local environment.
    """

    return settings.APP_SWITCHES["CELERY_BEAT_DEBUG_MODE"]


app.conf.beat_schedule = {
    "learning_retire": {
        "task": "apps.learning.tasks.learning_retire.handle_learning_retire",
        "schedule": crontab(minute="35", hour="5")  # every hour & every minute
        if is_beat_debug()
        else crontab(minute="35", hour="5"),  # every day 12.05 am,
    },
    "master_report_table": {
        "task": "apps.tenant.tasks.populate_tenant_master_report_table",
        "schedule": crontab(minute="35", hour="5")  # every hour & every minute
        if is_beat_debug()
        else crontab(minute="35", hour="5"),  # every day 12.05 am,
    },
    "enrollment_reminder": {
        "task": "apps.my_learning.tasks.enrollment_reminder.handle_enrollment_reminder_mail",
        "schedule": crontab(minute="35", hour="5")
        if is_beat_debug()
        else crontab(minute="35", hour="5"),  # every day 12.05 am,
    },
}
