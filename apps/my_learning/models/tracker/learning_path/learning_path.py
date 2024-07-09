from django.db import models
from django.db.models import Q

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.leaderboard.tasks import CommonLeaderboardTask
from apps.learning.models import LearningPath, LPAssessment, LPAssignment
from apps.my_learning.config import AllBaseLearningTypeChoices, LearningStatusChoices
from apps.my_learning.models import BaseUserTrackingModel
from apps.my_learning.models.tracker.assignment import AssignmentTracker
from apps.my_learning.models.tracker.learning_path.assessment import LPAssessmentTracker
from apps.tenant_service.middlewares import get_current_db_name


class UserLearningPathTracker(BaseUserTrackingModel):
    """User LeaningPath Tracking Model for IIHT-B2B"""

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_user_learning_path_trackers"

    learning_path = models.ForeignKey(
        to="learning.LearningPath", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    def call_leaderboard_task(self, milestone_names, request_headers=None):
        """Helper function to call leaderboard task."""

        db_name = get_current_db_name()
        if self.is_ccms_obj:
            extra_kwargs = {
                "is_ccms_obj": self.is_ccms_obj,
                "ccms_id": str(self.ccms_id),
            }
        else:
            extra_kwargs = {
                "learning_path_id": self.learning_path.id,
            }
        CommonLeaderboardTask().run_task(
            milestone_names=milestone_names,
            user_id=self.user.id,
            db_name=db_name,
            learning_type=AllBaseLearningTypeChoices.learning_path,
            request=request_headers,
            **extra_kwargs,
        )

    @classmethod
    def report_data(cls, learning_path, user):
        """Function to return user lp tracker details for report."""

        data = learning_path.report_data()
        data.update(**cls.get_default_report_data())
        lp_tracker = cls.objects.filter(learning_path=learning_path, user=user).first()
        if not lp_tracker:
            return data
        assessment_ids = LPAssessment.objects.filter(
            Q(learning_path=learning_path) | Q(lp_course__learning_path=learning_path)
        ).values_list("id", flat=True)
        assignment_ids = LPAssignment.objects.filter(
            Q(learning_path=learning_path) | Q(lp_course__learning_path=learning_path)
        ).values_list("assignment_id", flat=True)
        assessment_trackers_data = LPAssessmentTracker.assessment_report_data(user, assessment_ids)
        assignment_trackers_data = AssignmentTracker.assignment_report_data(user, assignment_ids)
        data.update(
            {
                "video_progress": lp_tracker.progress,
                "start_date": lp_tracker.created_at,
                "completion_date": lp_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if lp_tracker.is_completed
                else LearningStatusChoices.in_progress,
                **assessment_trackers_data,
                **assignment_trackers_data,
            }
        )
        return data

    @classmethod
    def ccms_report_data(cls, ccms_data, user):
        """Function to return user lp tracker details for report."""

        data = LearningPath.ccms_report_data(ccms_data["learning_path"])
        data.update(**cls.get_default_report_data())
        ccms_id = ccms_data["learning_path"]["uuid"]
        lp_tracker = cls.objects.filter(ccms_id=ccms_id, user=user).first()
        if not lp_tracker:
            return data
        assessment_trackers_data = LPAssessmentTracker.ccms_assessment_report_data(ccms_data["assessment"], lp_tracker)
        assignment_trackers_data = AssignmentTracker.ccms_assignment_report_data(ccms_data["assignment"], user)
        data.update(
            {
                "video_progress": lp_tracker.progress,
                "start_date": lp_tracker.created_at,
                "completion_date": lp_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if lp_tracker.is_completed
                else LearningStatusChoices.in_progress,
                **assessment_trackers_data,
                **assignment_trackers_data,
            }
        )
        return data
