from django.db import models
from django.db.models import Q

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.learning.models import Course, CourseAssessment, CourseAssignment
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import AssignmentTracker, BaseUserTrackingModel
from apps.my_learning.models.tracker.course.assessment import CourseAssessmentTracker
from apps.my_learning.models.tracker.course.sub_module import CourseSubModuleTracker


class UserCourseTracker(BaseUserTrackingModel):
    """
    User Course Tracking Model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, user, enrollment, course
        Fields      - uuid, ss_id, ccms_id
        Numeric     - completed_duration, progress
        Datetime    - last_accessed_on, created_at, modified_at,
        Boolean     - is_completed, is_ccms_obj

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_user_course_trackers"

    course = models.ForeignKey(
        to="learning.Course", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    @classmethod
    def report_data(cls, course, user):
        """Function to return user course tracker details for report."""

        data = course.report_data()
        data.update(**cls.get_default_report_data())
        course_tracker = cls.objects.filter(course=course, user=user).first()
        if not course_tracker:
            return data
        assessment_ids = CourseAssessment.objects.filter(Q(course=course) | Q(module__course=course)).values_list(
            "id", flat=True
        )
        assignment_ids = CourseAssignment.objects.filter(Q(course=course) | Q(module__course=course)).values_list(
            "assignment_id", flat=True
        )
        sub_module_trackers_data = CourseSubModuleTracker.file_submission_report_data(course_tracker)
        assessment_trackers_data = CourseAssessmentTracker.assessment_report_data(course_tracker, assessment_ids)
        assignment_trackers_data = AssignmentTracker.assignment_report_data(user, assignment_ids)
        combined_assignment_data = {}
        for key in assignment_trackers_data:
            combined_assignment_data[key] = (assignment_trackers_data[key] or []) + (
                sub_module_trackers_data[key] or []
            )
        data.update(
            {
                "video_progress": course_tracker.progress,
                "start_date": course_tracker.created_at,
                "completion_date": course_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if course_tracker.is_completed
                else LearningStatusChoices.in_progress,
                **assessment_trackers_data,
                **combined_assignment_data,
            }
        )
        return data

    @classmethod
    def ccms_report_data(cls, ccms_data, user):
        """Function to return ccms user course tracker details for report."""

        data = Course.ccms_report_data(ccms_data["course"])
        data.update(**cls.get_default_report_data())
        ccms_id = data["course_uuid"]
        course_tracker = cls.objects.filter(ccms_id=ccms_id, user=user).first()
        if course_tracker:
            assessment_trackers_data = CourseAssessmentTracker.ccms_assessment_report_data(
                ccms_data["assessment"], course_tracker
            )
            sub_module_trackers_data = CourseSubModuleTracker.ccms_file_submission_report_data(
                ccms_data["sub_module"], course_tracker
            )
            assignment_trackers_data = AssignmentTracker.ccms_assignment_report_data(ccms_data["assignment"], user)
            combined_assignment_data = {}
            for key in assignment_trackers_data:
                combined_assignment_data[key] = (assignment_trackers_data[key] or []) + (
                    sub_module_trackers_data[key] or []
                )
            data.update(
                {
                    "video_progress": course_tracker.progress,
                    "start_date": course_tracker.created_at,
                    "completion_date": course_tracker.completion_date,
                    "learning_status": LearningStatusChoices.completed
                    if course_tracker.is_completed
                    else LearningStatusChoices.in_progress,
                    **assessment_trackers_data,
                    **combined_assignment_data,
                }
            )
        return data
