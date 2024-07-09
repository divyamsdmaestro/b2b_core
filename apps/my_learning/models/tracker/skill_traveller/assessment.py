from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.my_learning.models import BaseAssessmentTrackingModel, BaseYakshaResult, BaseYakshaSchedule


class STAssessmentTracker(BaseAssessmentTrackingModel):
    """
    Tracker model for IIHT-B2B skill_traveller assessments.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, assessment
        Fields      - uuid, ss_id,
        Numeric     - progress, available_attempt
        Bool        - is_pass,
        Datetime    - created_at, modified_at, start_date, completion_date, last_accessed_on

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseAssessmentTrackingModel.Meta):
        default_related_name = "related_st_assessment_trackers"

    assessment = models.ForeignKey(
        to="learning.STAssessment", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    user = models.ForeignKey(to="access.User", on_delete=models.CASCADE)

    @classmethod
    def assessment_report_data(cls, user, assessment_ids):
        """Function to get the st assessment report data."""

        st_assessment_trackers = cls.objects.filter(user=user, assessment__in=assessment_ids)
        availed_attempts, progress, results, scores = [], [], [], []
        for tracker in st_assessment_trackers:
            if yaksha_schedules := tracker.related_sta_yaksha_schedules.first():
                if result := yaksha_schedules.related_sta_yaksha_results.order_by("-progress").first():
                    name = tracker.assessment.name
                    if tracker.allowed_attempt is not None and tracker.available_attempt is not None:
                        attempt = (
                            tracker.allowed_attempt
                            + getattr(tracker, "reattempt_count", 0)
                            - tracker.available_attempt
                        )
                        availed_attempts.append(f"{name} - {attempt}")
                    if result.is_pass:
                        progress.append(f"{name} - 100")
                        results.append(f"{name} - Passed")
                    else:
                        progress.append(f"{name} - 100")
                        results.append(f"{name} - Failed")
                    scores.append(f"{name} - {result.progress}")
        return {
            "assessment_availed_attempts": availed_attempts if availed_attempts else None,
            "assessment_progress": progress if progress else None,
            "assessment_result": results if results else None,
            "assessment_score": scores if scores else None,
        }


class STAYakshaSchedule(BaseYakshaSchedule):
    """
    skill traveller assessment yaksha schedule model.

    ********************* Model Fields *********************
        PK          - id
        FK          - user, tracker
        Unique      - uuid, ss_id, scheduled_id
        URL         - scheduled_link
        Datetime    - created_at, modified_at
    """

    class Meta(BaseYakshaSchedule.Meta):
        default_related_name = "related_sta_yaksha_schedules"

    tracker = models.ForeignKey(STAssessmentTracker, models.CASCADE)


class STAYakshaResult(BaseYakshaResult):
    """
    Yaksha Result model for skill_traveller assessments.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id
        FK          - schedule
        Datetime    - created_at, modified_at
        Numeric     - attempt, duration, total_questions, answered, progress,
        DateTime    - start_time, end_time
        Bool        - is_pass
    """

    class Meta(BaseYakshaResult.Meta):
        default_related_name = "related_sta_yaksha_results"

    schedule = models.ForeignKey(STAYakshaSchedule, on_delete=models.CASCADE)
