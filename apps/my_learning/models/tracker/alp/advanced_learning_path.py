from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.leaderboard.tasks import CommonLeaderboardTask
from apps.learning.models import AdvancedLearningPath
from apps.my_learning.config import AllBaseLearningTypeChoices, LearningStatusChoices
from apps.my_learning.models import BaseUserTrackingModel
from apps.tenant_service.middlewares import get_current_db_name


class UserALPTracker(BaseUserTrackingModel):
    """User AdvancedLeaningPath Tracking Model for IIHT-B2B."""

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_user_alp_trackers"

    advanced_learning_path = models.ForeignKey(
        to="learning.AdvancedLearningPath", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
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
                "advanced_learning_path_id": self.advanced_learning_path.id,
            }
        CommonLeaderboardTask().run_task(
            milestone_names=milestone_names,
            user_id=self.user.id,
            db_name=db_name,
            learning_type=AllBaseLearningTypeChoices.advanced_learning_path,
            request=request_headers,
            **extra_kwargs,
        )

    @classmethod
    def report_data(cls, advanced_learning_path, user):
        """Function to return user alp tracker details for report."""

        data = advanced_learning_path.report_data()
        data.update(**cls.get_default_report_data())
        alp_tracker = cls.objects.filter(advanced_learning_path=advanced_learning_path, user=user).first()
        if not alp_tracker:
            return data
        data.update(
            {
                "video_progress": alp_tracker.progress,
                "start_date": alp_tracker.created_at,
                "completion_date": alp_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if alp_tracker.is_completed
                else LearningStatusChoices.in_progress,
            }
        )
        return data

    @classmethod
    def ccms_report_data(cls, ccms_data, user):
        """Function to return user alp tracker details for report."""

        data = AdvancedLearningPath.ccms_report_data(ccms_data["advanced_learning_path"])
        data.update(**cls.get_default_report_data())
        ccms_id = ccms_data["advanced_learning_path"]["uuid"]
        alp_tracker = cls.objects.filter(ccms_id=ccms_id, user=user).first()
        if not alp_tracker:
            return data
        data.update(
            {
                "video_progress": alp_tracker.progress,
                "start_date": alp_tracker.created_at,
                "completion_date": alp_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if alp_tracker.is_completed
                else LearningStatusChoices.in_progress,
            }
        )
        return data
