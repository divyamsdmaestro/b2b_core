from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.learning.config import PlaygroundToolChoices
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import BaseFileSubmission, BaseUserTrackingModel, BaseYakshaResult, BaseYakshaSchedule


class AssignmentTracker(BaseUserTrackingModel):
    """
    Assignment tracker model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, enrollment, user, assignment
        Fields      - uuid, ss_id,
        Numeric     - progress, available_attempt
        Bool        - is_pass,
        Datetime    - created_at, modified_at, start_date, completion_date, last_accessed_on

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_assignment_trackers"

    assignment = models.ForeignKey(
        to="learning.Assignment", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    allowed_attempt = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    available_attempt = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_pass = models.BooleanField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    start_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def assignment_relation_progress_update(self):
        """updates the assignment progress."""

        assignment_relations = self.assignment.related_assignment_relations.all()
        for assignment_relation in assignment_relations:
            if assignment_group_tracker := assignment_relation.assignment_group.related_assignment_group_trackers.filter(  # noqa
                user=self.user
            ).first():
                assignment_group_tracker.assignment_group_progress_update()
        return True

    @classmethod
    def report_data(cls, assignment, user):
        """Function to return user assignment tracker details for report."""

        data = assignment.report_data()
        data.update(**cls.get_default_report_data())
        assignment_tracker = cls.objects.filter(assignment=assignment, user=user).first()
        if not assignment_tracker:
            return data
        assignment_trackers_data = cls.assignment_report_data(user, [assignment.id])
        data.update(
            {
                "video_progress": assignment_tracker.progress,
                "start_date": assignment_tracker.created_at,
                "completion_date": assignment_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if assignment_tracker.is_completed
                else LearningStatusChoices.in_progress,
                **assignment_trackers_data,
            }
        )
        return data

    @classmethod
    def assignment_report_data(cls, user, assignment_ids):
        """Function to return learning assignment data."""

        assignment_trackers = cls.objects.filter(user=user, assignment__in=assignment_ids, is_completed=True)
        results, progress, scores = [], [], []
        for tracker in assignment_trackers:
            assignment, score = tracker.assignment, "N/A"
            if assignment.tool == PlaygroundToolChoices.yaksha:
                if yaksha_schedule := tracker.related_assignment_yaksha_schedules.first():
                    if assessment_result := yaksha_schedule.related_assignment_yaksha_results.order_by(
                        "-progress"
                    ).first():
                        score = assessment_result.progress
            elif assignment.tool == PlaygroundToolChoices.mml:
                if submission := tracker.related_assignment_submissions.order_by("-progress").first():
                    score = submission.progress
            name = assignment.name
            submission_status, submission_progress = ("Passed", 100) if tracker.is_pass else ("Failed", 0)
            results.append(f"{name} - {submission_status}")
            progress.append(f"{name} - {submission_progress}")
            scores.append(f"{name} - {score}")
        return {
            "assignment_result": results if results else None,
            "assignment_score": scores if scores else None,
            "assignment_progress": progress if progress else None,
        }

    @classmethod
    def ccms_assignment_report_data(cls, assignment_data, user):
        """Function to return ccms learning assignment data."""

        results, progress, scores = [], [], []
        for assignment in assignment_data:
            tracker = (
                cls.objects.filter(is_completed=True, user=user, ccms_id=assignment["assignment"]["uuid"])
                .order_by("-progress")
                .first()
            )
            if not tracker:
                return {}
            tool = assignment["assignment"]["tool"]
            name = assignment["assignment"]["name"]
            score = "N/A"
            if tool == PlaygroundToolChoices.yaksha:
                if yaksha_schedule := tracker.related_assignment_yaksha_schedules.first():
                    if assessment_result := yaksha_schedule.related_assignment_yaksha_results.order_by(
                        "-progress"
                    ).first():
                        score = assessment_result.progress
            elif tool == PlaygroundToolChoices.mml:
                if submission := tracker.related_assignment_submissions.order_by("-progress").first():
                    score = submission.progress
            submission_status, submission_progress = ("Passed", 100) if tracker.is_pass else ("Failed", 0)
            results.append(f"{name} - {submission_status}")
            progress.append(f"{name} - {submission_progress}")
            scores.append(f"{name} - {score}")
        return {
            "assignment_result": results if results else None,
            "assignment_score": scores if scores else None,
            "assignment_progress": progress if progress else None,
        }


class AssignmentSubmission(BaseFileSubmission):
    """
    Assignment submission model.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id
        FK          - assignment_tracker, evaluator
        M2M         - files
        Fields      - description, feedback
        Numeric     - attempt, progress,
        Datetime    - created_at, modified_at
        Bool        - is_pass, is_reviewed
    """

    class Meta(BaseFileSubmission.Meta):
        default_related_name = "related_assignment_submissions"

    assignment_tracker = models.ForeignKey(to=AssignmentTracker, on_delete=models.CASCADE)


class AssignmentYakshaSchedule(BaseYakshaSchedule):
    """
    Common model for yaksha assessment schedules.

    ********************* Model Fields *********************
        PK          - id
        FK          - assignment_tracker
        Unique      - uuid, ss_id, scheduled_id
        URL         - scheduled_link
        Datetime    - created_at, modified_at
    """

    class Meta(BaseYakshaSchedule.Meta):
        default_related_name = "related_assignment_yaksha_schedules"

    assignment_tracker = models.ForeignKey(AssignmentTracker, models.CASCADE)


class AssignmentYakshaResult(BaseYakshaResult):
    """
    Common model for yaksha assessment results.

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
        default_related_name = "related_assignment_yaksha_results"

    schedule = models.ForeignKey(AssignmentYakshaSchedule, on_delete=models.CASCADE)
