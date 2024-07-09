from django.db import models
from django.utils import timezone

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.my_learning.config import AllBaseLearningTypeChoices, LearningStatusChoices
from apps.my_learning.models import BaseUserTrackingModel
from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress


class AssignmentGroupTracker(BaseUserTrackingModel):
    """
    User Assignment Group Tracking Model for IIHT-B2B.
    Model Fields -
        PK          - id,
        Fk          - created_by, assignment_group, enrolled_to
        Fields      - uuid, ss_id, actionee, action, reason
        Numeric     - progress
        Datetime    - valid_till, last_accessed_on, created_at, modified_at, action_date
        Bool        - is_started, is_completed,is_tenant_admin_approval, is_super_admin_approval, is_self_enrolled,

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_assignment_group_trackers"

    assignment_group = models.ForeignKey(
        to="learning.AssignmentGroup", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    def assignment_group_progress_update(self):
        """Update the assignment group progress based on the assignment progress."""

        related_assignments = self.assignment_group.related_assignment_relations.all()
        assignment_progress_list = []
        for assignment_group in related_assignments:
            assignment_tracker = assignment_group.assignment.related_assignment_trackers.filter(user=self.user).first()
            assignment_progress_list.append(assignment_tracker.progress if assignment_tracker else 0)
        progress = (
            round(sum(assignment_progress_list) / len(assignment_progress_list)) if assignment_progress_list else 0
        )
        if not self.is_completed:
            self.progress = get_actual_progress(self.progress, progress)
            if progress == 100:
                self.is_completed = True
                self.enrollment.learning_status = LearningStatusChoices.completed
                self.completion_date = timezone.now()
                self.enrollment.save()
        self.last_accessed_on = timezone.now()
        self.save()
        if not self.is_ccms_obj:
            self.user.related_skill_ontology_progress_update(
                AllBaseLearningTypeChoices.assignment_group, self.assignment_group
            )
        return self

    @classmethod
    def report_data(cls, assignment_group, user):
        """Function to return user ag tracker details for report."""

        data = assignment_group.report_data()
        data.update(**cls.get_default_report_data())
        ag_tracker = cls.objects.filter(assignment_group=assignment_group, user=user).first()
        if not ag_tracker:
            return data
        data.update(
            {
                "video_progress": ag_tracker.progress,
                "start_date": ag_tracker.created_at,
                "completion_date": ag_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if ag_tracker.is_completed
                else LearningStatusChoices.in_progress,
            }
        )
        return data
