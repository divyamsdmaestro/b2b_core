from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.my_learning.models import BaseAssessmentTrackingModel, BaseYakshaResult, BaseYakshaSchedule


class LPAssessmentTracker(BaseAssessmentTrackingModel):
    """
    Tracker model for IIHT-B2B learning_path assessments.

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
        default_related_name = "related_lp_assessment_trackers"

    assessment = models.ForeignKey(
        to="learning.LPAssessment", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    user = models.ForeignKey(to="access.User", on_delete=models.CASCADE)

    @classmethod
    def assessment_report_data(cls, user, assessment_ids):
        """Function to get the lp assessment report data."""

        lp_assessment_trackers = cls.objects.filter(user=user, assessment__in=assessment_ids)
        availed_attempts, progress, results, scores = [], [], [], []
        total_score = 0
        for tracker in lp_assessment_trackers:
            if yaksha_schedules := tracker.related_lpa_yaksha_schedules.first():
                if result := yaksha_schedules.related_lpa_yaksha_results.order_by("-progress").first():
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
                    total_score += result.progress
                    scores.append(f"{name} - {result.progress}")
        return {
            "assessment_availed_attempts": availed_attempts if availed_attempts else None,
            "assessment_progress": progress if progress else None,
            "assessment_result": results if results else None,
            "assessment_score": scores if scores else None,
            "average_assessment_score": total_score / len(scores) if len(scores) > 0 else None,
        }

    @classmethod
    def ccms_assessment_report_data(cls, assessment_data, lp_tracker):
        """Function to get the lp assessment report data."""

        availed_attempts, progress, results, scores = [], [], [], []
        total_score = 0
        user = lp_tracker.user
        assessment_ids, assessment_details = [], {}
        for assessment in assessment_data:
            assessment_ids.append(assessment["uuid"])
            assessment_details[assessment["uuid"]] = assessment["name"]
        lp_assessment_trackers = user.related_lp_assessment_trackers.filter(ccms_id__in=assessment_ids)
        for tracker in lp_assessment_trackers:
            if yaksha_schedules := tracker.related_lpa_yaksha_schedules.first():
                if result := yaksha_schedules.related_lpa_yaksha_results.order_by("-progress").first():
                    name = assessment_details.get(str(tracker.ccms_id))
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
                    total_score += result.progress
                    scores.append(f"{name} - {result.progress}")
        return {
            "assessment_availed_attempts": availed_attempts if availed_attempts else None,
            "assessment_progress": progress if progress else None,
            "assessment_result": results if results else None,
            "assessment_score": scores if scores else None,
            "average_assessment_score": total_score / len(scores) if len(scores) > 0 else None,
        }


class LPAYakshaSchedule(BaseYakshaSchedule):
    """
    Learning path assessment yaksha schedule model.

    ********************* Model Fields *********************
        PK          - id
        FK          - user, tracker
        Unique      - uuid, ss_id, scheduled_id
        URL         - scheduled_link
        Datetime    - created_at, modified_at
    """

    class Meta(BaseYakshaSchedule.Meta):
        default_related_name = "related_lpa_yaksha_schedules"

    tracker = models.ForeignKey(LPAssessmentTracker, models.CASCADE)


class LPAYakshaResult(BaseYakshaResult):
    """
    Yaksha Result model for learning_path assessments.

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
        default_related_name = "related_lpa_yaksha_results"

    schedule = models.ForeignKey(LPAYakshaSchedule, on_delete=models.CASCADE)
