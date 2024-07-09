from django.db import models

from apps.common.models.base import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.learning.config import EvaluationTypeChoices, SubModuleTypeChoices
from apps.my_learning.models import BaseFileSubmission, BaseTrackingModel


class CourseSubModuleTracker(BaseTrackingModel):
    """
    CourseSubModule Tracking Model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, sub_module, module_tracker
        Fields      - uuid, ss_id
        Numeric     - completed_duration, progress, available_attempt
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseTrackingModel.Meta):
        default_related_name = "related_course_sub_module_trackers"

    sub_module = models.ForeignKey(
        "learning.CourseSubModule", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    module_tracker = models.ForeignKey("my_learning.CourseModuleTracker", on_delete=models.CASCADE)
    available_attempt = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    @classmethod
    def file_submission_report_data(cls, course_tracker):
        """Function to return course assessment data."""

        sub_module_trackers = cls.objects.filter(
            sub_module__type=SubModuleTypeChoices.file_submission,
            module_tracker__course_tracker=course_tracker,
        )
        results, progress, scores = [], [], []
        for tracker in sub_module_trackers:
            if submission := tracker.related_sub_module_submissions.order_by("-progress").first():
                sub_module = submission.sub_module_tracker.sub_module
                name = sub_module.name
                if sub_module.evaluation_type == EvaluationTypeChoices.evaluated:
                    if submission.is_reviewed:
                        submission_status, submission_progress = (
                            ("Passed", 100) if submission.is_pass else ("Failed", 0)
                        )
                        submission_score = submission.progress
                    else:
                        submission_status = "Evaluation Pending"
                        submission_progress = submission_score = "N/A"
                else:
                    submission_status, submission_progress, submission_score = "Passed", 100, "N/A"
                results.append(f"{name} - {submission_status}")
                progress.append(f"{name} - {submission_progress}")
                scores.append(f"{name} - {submission_score}")
        return {
            "assignment_result": results if results else None,
            "assignment_score": scores if scores else None,
            "assignment_progress": progress if progress else None,
        }

    @classmethod
    def ccms_file_submission_report_data(cls, sub_module_data, course_tracker):
        """Function to return course assessment data."""

        sub_module_ids, sub_module_details = [], {}
        for sub_module in sub_module_data:
            if sub_module["type"]["id"] == "file_submission":
                sub_module_uuid = sub_module["uuid"]
                sub_module_ids.append(sub_module_uuid)
                sub_module_details[sub_module_uuid] = {
                    "name": sub_module["name"],
                    "evaluation_type": sub_module["evaluation_type"],
                }
        sub_module_trackers = CourseSubModuleTracker.objects.filter(
            ccms_id__in=sub_module_ids,
            module_tracker__course_tracker=course_tracker,
        )
        results, progress, scores = [], [], []
        for tracker in sub_module_trackers:
            if submission := tracker.related_sub_module_submissions.order_by("-progress").first():
                sub_module_uuid = submission.sub_module_tracker.ccms_id
                evaluation_type = sub_module_details[str(sub_module_uuid)]["evaluation_type"]
                name = sub_module_details[str(sub_module_uuid)]["name"]
                if evaluation_type == EvaluationTypeChoices.evaluated:
                    if submission.is_reviewed:
                        submission_status, submission_progress = (
                            ("Passed", 100) if submission.is_pass else ("Failed", 0)
                        )
                        submission_score = submission.progress
                    else:
                        submission_status = "Evaluation Pending"
                        submission_progress = submission_score = "N/A"
                else:
                    submission_status, submission_progress, submission_score = "Passed", 100, "N/A"
                results.append(f"{name} - {submission_status}")
                progress.append(f"{name} - {submission_progress}")
                scores.append(f"{name} - {submission_score}")
        return {
            "assignment_result": results if results else None,
            "assignment_score": scores if scores else None,
            "assignment_progress": progress if progress else None,
        }


class SubModuleFileSubmission(BaseFileSubmission):
    """
    SubModule file submission model.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id
        FK          - sub_module_tracker, evaluator
        M2M         - files
        Fields      - description, feedback
        Numeric     - progress,
        Datetime    - created_at, modified_at
        Bool        - is_pass, is_reviewed
    """

    class Meta(BaseFileSubmission.Meta):
        default_related_name = "related_sub_module_submissions"

    sub_module_tracker = models.ForeignKey(to=CourseSubModuleTracker, on_delete=models.CASCADE)
