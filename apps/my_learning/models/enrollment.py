from django.db import models
from django.template import Context, Template
from django.utils.html import strip_tags

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    CreationAndModificationModel,
)
from apps.common.tasks.outbound import SendEmailTask
from apps.event.config import CalendarEventTypeChoices
from apps.event.models import CalendarActivity
from apps.leaderboard.config import MilestoneChoices
from apps.leaderboard.tasks import CommonLeaderboardTask
from apps.mailcraft.config import TemplateFieldChoices
from apps.my_learning.config import (
    ActionChoices,
    AllBaseLearningTypeChoices,
    ApprovalTypeChoices,
    EnrollmentTypeChoices,
    LearningStatusChoices,
)
from apps.my_learning.models import BaseLearningFKModel
from apps.tenant_service.middlewares import get_current_db_name


class Enrollment(CreationAndModificationModel, BaseLearningFKModel):
    """Model to store user & user group enrollments."""

    class Meta(CreationAndModificationModel.Meta):
        default_related_name = "related_enrollments"

    # FK fields
    user_group = models.ForeignKey(
        "access_control.UserGroup",
        on_delete=models.CASCADE,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # Choices
    learning_type = models.CharField(
        choices=EnrollmentTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    # Fields
    actionee = models.ForeignKey(
        to="access.User",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        related_name="related_enrollment_actionee",
    )
    reason = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    action_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    action = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=ActionChoices.choices, default=ActionChoices.pending
    )
    learning_status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=LearningStatusChoices.choices,
        default=LearningStatusChoices.not_started,
    )
    approval_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=ApprovalTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    is_enrolled = models.BooleanField(default=False)
    start_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def call_leaderboard_tasks(self, is_assigned=None, request_headers=None):
        """Call leaderboard tasks based on course enrollment."""

        db_name = get_current_db_name()
        if self.is_ccms_obj:
            extra_kwargs = {"is_ccms_obj": self.is_ccms_obj, "ccms_id": str(self.ccms_id)}
        else:
            extra_kwargs = {f"{self.learning_type}_id": getattr(self, self.learning_type).id}
        actions = self.get_actions()
        if not actions:
            return False
        milestones = [actions["first_enroll_milestone"]]
        if is_assigned:
            milestones.append(actions["assigned_enrollment_milestone"])
        else:
            milestones.append(actions["self_enroll_milestone"])
        CommonLeaderboardTask().run_task(
            milestone_names=milestones,
            user_id=self.user.id,
            db_name=db_name,
            request=request_headers,
            learning_type=self.learning_type,
            **extra_kwargs,
        )
        return True

    def notify_user(self, ccms_obj_name=None):
        """Send notification to user about enrollments."""

        from apps.notification.models import Notification

        if not self.is_enrolled:
            return False
        if self.is_ccms_obj:
            extra_kwargs = {"is_ccms_obj": self.is_ccms_obj, "ccms_id": str(self.ccms_id), "obj_name": ccms_obj_name}
        else:
            extra_kwargs = {
                f"{self.learning_type}_id": getattr(self, self.learning_type).id,
                "obj_name": getattr(self, self.learning_type).name,
            }
        actions = self.get_actions(is_notification=True)
        if not actions:
            return False
        if self.approval_type == ApprovalTypeChoices.self_enrolled:
            action = actions["self_enroll_action"]
        else:
            action = actions["assigned_action"]
        if self.user:
            Notification.notify_user(user=self.user, action=action, **extra_kwargs)
        else:
            for user in self.user_group.members.all():
                Notification.notify_user(user=user, action=action, **extra_kwargs)

    def get_actions(self, is_notification=False):
        """DRY function to get appropriate actions based on learning_type."""

        from apps.notification.config import NotifyActionChoices

        match self.learning_type:
            case EnrollmentTypeChoices.course:
                first_enroll_milestone = MilestoneChoices.first_course_enroll
                self_enroll_milestone = MilestoneChoices.course_self_enroll
                assigned_enrollment_milestone = MilestoneChoices.course_assigned
                self_enroll_action = NotifyActionChoices.self_course_enroll
                assigned_action = NotifyActionChoices.course_assigned
            case EnrollmentTypeChoices.learning_path:
                first_enroll_milestone = MilestoneChoices.first_learning_path_enroll
                self_enroll_milestone = MilestoneChoices.learning_path_self_enroll
                assigned_enrollment_milestone = MilestoneChoices.learning_path_assigned
                self_enroll_action = NotifyActionChoices.self_lp_enroll
                assigned_action = NotifyActionChoices.lp_assigned
            case EnrollmentTypeChoices.advanced_learning_path:
                first_enroll_milestone = MilestoneChoices.first_certification_path_enrollment
                self_enroll_milestone = MilestoneChoices.certification_path_self_enrolled
                assigned_enrollment_milestone = MilestoneChoices.certification_path_assigned
                self_enroll_action = NotifyActionChoices.self_alp_enroll
                assigned_action = NotifyActionChoices.alp_assigned
            case EnrollmentTypeChoices.skill_ontology:
                self_enroll_action = NotifyActionChoices.skill_ontology_enroll
                assigned_action = None
            case _:
                return False
        if is_notification:
            actions = {"self_enroll_action": self_enroll_action, "assigned_action": assigned_action}
        else:
            actions = {
                "first_enroll_milestone": first_enroll_milestone,
                "self_enroll_milestone": self_enroll_milestone,
                "assigned_enrollment_milestone": assigned_enrollment_milestone,
            }
        return actions

    def remove_dependencies(self):
        """Function to remove the calendar events for this enrolled learning instance."""

        if self.is_ccms_obj:
            return True
        if self.user:
            user_ids = [self.user.id]
        elif self.user_group:
            user_ids = self.user_group.members.all().values_list("id", flat=True)
        else:
            return False
        match self.learning_type:
            case EnrollmentTypeChoices.course:
                event_subtypes = [CalendarEventTypeChoices.session, CalendarEventTypeChoices.course]
            case EnrollmentTypeChoices.learning_path:
                event_subtypes = [CalendarEventTypeChoices.learning_path]
            case EnrollmentTypeChoices.advanced_learning_path:
                event_subtypes = [
                    CalendarEventTypeChoices.advanced_learning_path,
                    CalendarEventTypeChoices.alp_learning_path,
                ]
            case _:
                return False
        CalendarActivity.objects.filter(
            event_subtype__in=event_subtypes,
            event_subtype_id=getattr(self, self.learning_type).id,
            user_id__in=user_ids,
        ).delete()
        return True

    def report_data(self):
        """Function to return enrollment details for report."""

        return {
            "learning_type": self.learning_type,
            "approval_type": self.approval_type,
            "end_date": self.end_date,
            "is_user_group_enrollment": True if self.user_group else False,
            "enrolled_user_group_name": self.user_group.name if self.user_group else None,
        }

    def ccms_learning_data(self):
        """Report data for respective ccms learning."""

        from apps.learning.helpers import get_ccms_retrieve_details

        success, data = get_ccms_retrieve_details(
            learning_type=f"core_{self.learning_type}",
            instance_id=str(self.ccms_id),
            request=None,
            is_default_creds=True,
            use_cache=True,
        )
        if not success or not data.get("data"):
            return None
        return data["data"]

    def learning_tracker_report_data(self, learning_type, learning_obj, user):
        """Function to return enrollment learning tracker data."""

        from apps.my_learning.models import (
            AssignmentGroupTracker,
            AssignmentTracker,
            UserALPTracker,
            UserCourseTracker,
            UserLearningPathTracker,
            UserSkillOntologyTracker,
            UserSkillTravellerTracker,
        )

        match learning_type:
            case EnrollmentTypeChoices.course:
                return UserCourseTracker.report_data(learning_obj, user)
            case EnrollmentTypeChoices.learning_path:
                return UserLearningPathTracker.report_data(learning_obj, user)
            case EnrollmentTypeChoices.advanced_learning_path:
                return UserALPTracker.report_data(learning_obj, user)
            case EnrollmentTypeChoices.skill_traveller:
                return UserSkillTravellerTracker.report_data(learning_obj, user)
            case EnrollmentTypeChoices.assignment:
                return AssignmentTracker.report_data(learning_obj, user)
            case EnrollmentTypeChoices.assignment_group:
                return AssignmentGroupTracker.report_data(learning_obj, user)
            case EnrollmentTypeChoices.skill_ontology:
                return UserSkillOntologyTracker.report_data(learning_obj, user)
        return {}

    def ccms_learning_tracker_report_data(self, learning_type, data, user):
        """Function to return ccms enrollment learning tracker data."""

        from apps.my_learning.models import (
            AssignmentTracker,
            UserALPTracker,
            UserCourseTracker,
            UserLearningPathTracker,
        )

        match learning_type:
            case EnrollmentTypeChoices.course:
                return UserCourseTracker.ccms_report_data(data, user)
            case EnrollmentTypeChoices.learning_path:
                return UserLearningPathTracker.ccms_report_data(data, user)
            case EnrollmentTypeChoices.advanced_learning_path:
                return UserALPTracker.ccms_report_data(data, user)
            case EnrollmentTypeChoices.assignment:
                return AssignmentTracker.ccms_assignment_report_data(data, user)
        return {}

    def trigger_enrollment_reminder_email(self, user, **kwargs):
        """Function to trigger enrollment reminder email for learners."""

        from apps.my_learning.helpers import get_tracker_instance

        tracker = get_tracker_instance(user, self)
        if tracker and tracker.is_completed:
            return True
        artifact_name = "CCMS" if self.is_ccms_obj else getattr(self, self.learning_type).name
        mail_template = kwargs["mail_template"]
        email_context = {
            TemplateFieldChoices.user_name: user.name,
            TemplateFieldChoices.artifact_type: self.learning_type,
            TemplateFieldChoices.artifact_name: artifact_name,
            TemplateFieldChoices.artifact_progress: getattr(tracker, "progress", 0),
            TemplateFieldChoices.end_date: self.end_date,
            TemplateFieldChoices.website_url: kwargs.get("url"),
        }
        template = Template(mail_template.content)
        html_body = template.render(Context(email_context))
        SendEmailTask().run_task(
            subject=mail_template.subject,
            message=strip_tags(html_body),
            recipients=[user.email],
            sender_email=kwargs["sender_email"],
            html_message=html_body,
        )
        return True


class EnrollmentReminder(BaseModel):
    """
    Model to store Enrollment Reminder

        PK      - id,
        Choices - learning_type
        Fields  - uuid, days

    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_enrollment_reminders"

    learning_type = models.CharField(
        choices=AllBaseLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        unique=True,
    )
    days = models.PositiveIntegerField()
