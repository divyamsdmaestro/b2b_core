from django.db import models
from django.utils import timezone

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.learning.config import EvaluationTypeChoices
from apps.learning.models import CourseAssessment, CourseAssignment
from apps.my_learning.models import BaseTrackingModel, CourseAssessmentTracker


class CourseModuleTracker(BaseTrackingModel):
    """
    CourseModule Tracking Model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, module, course_tracker
        Fields      - uuid, ccms_module
        Datetime    - created_at, modified_at
        Numeric     - completed_duration, progress
        Bool        - is_ccms_obj

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta(BaseTrackingModel.Meta):
        default_related_name = "related_course_module_trackers"

    module = models.ForeignKey(
        "learning.CourseModule", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    course_tracker = models.ForeignKey("my_learning.UserCourseTracker", on_delete=models.CASCADE)

    def previous_modules(self):
        """Returns previous modules & assignment was not completed."""

        previous_modules = CourseModuleTracker.objects.filter(
            course_tracker=self.course_tracker, module__sequence__lt=self.module.sequence or 0
        ).exclude(id=self.pk)
        previous_module_id = previous_modules.values_list("module__id", flat=True)
        previous_assessment_objs = CourseAssessment.objects.filter(
            module_id__in=previous_module_id, is_practice=False
        ).values_list("id", flat=True)
        previous_assessment_tracker_qs = CourseAssessmentTracker.objects.filter(
            assessment_id__in=previous_assessment_objs
        )
        uncompleted_assessment = previous_assessment_tracker_qs.filter(is_completed=False).first()
        previous_assignment_objs = CourseAssignment.objects.filter(
            module_id__in=previous_module_id, assignment__evaluation_type=EvaluationTypeChoices.evaluated
        ).values_list("assignment_id", flat=True)
        previous_assignment_tracker_qs = self.course_tracker.user.related_assignment_trackers.filter(
            assignment_id__in=previous_assignment_objs
        )
        uncompleted_assignment = previous_assignment_tracker_qs.filter(is_completed=False).first()
        return (
            previous_modules,
            previous_assessment_tracker_qs.count() == previous_assessment_objs.count(),
            True if uncompleted_assessment else False,
            previous_assignment_tracker_qs.count() == previous_assignment_objs.count(),
            True if uncompleted_assignment else False,
        )

    @property
    def is_locked(self):
        """
        If the module is sequential then locking system should be enabled. Logic for the same.
        If the module is mandatory and all the previous mandatory models are completed only
        then the current module should be opened otherwise it should be locked
        irrespective of start/end date. If module is not mandatory then it
        can be opened/skipped. As per iiht @Darshan on 09-11-23.

        Used in serializer
        """

        if self.course_tracker.is_completed or self.is_completed:
            return False
        if (
            self.module.start_date
            and self.module.end_date
            and not self.module.start_date <= timezone.now().date() <= self.module.end_date
        ):
            return True
        (
            previous_modules,
            is_assessment_tracker,
            uncompleted_assessment,
            is_assignment_tracker,
            uncompleted_assignment,
        ) = self.previous_modules()
        if not previous_modules.exists():
            return False
        elif self.module.course.is_dependencies_sequential and (
            previous_modules.filter(is_completed=False).exists()
            or not is_assessment_tracker
            or uncompleted_assessment
            or not is_assignment_tracker
            or uncompleted_assignment
        ):
            return True
        return False
