# flake8: noqa
from .common import BaseLearningEmailTask
from .enrollment_email import UserEnrollmentEmailTask
from .playground import PlaygroundTrackingTask
from .playground_group import PlaygroundGroupEnrollmentTask, PlaygroundGroupTrackingTask
from .user_enrollment import UserBulkEnrollTask
from .activity import CalendarActivityCreationTask
from .bulk_enrollment import EnrollmentBulkUploadTask, BulkUnenrollmentTask
from .report import (
    FileSubmissionReportGenerationTask,
    ReportGenerationTask,
    LeaderboardReportGenerationTask,
    FeedbackReportGenerationTask,
)
from apps.my_learning.tasks.progress.course import CourseProgressUpdateTask
from apps.my_learning.tasks.progress.learning_path import LPProgressUpdateTask
from .skill_ontology import SkillOntologyProgressUpdateTask
from apps.my_learning.tasks.progress.advanced_learning_path import ALPProgressUpdateTask
from .enrollment_reminder import handle_enrollment_reminder_mail
