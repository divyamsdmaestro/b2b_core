from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.learning.models.skill_traveller.assessment import STAssessment
from apps.learning.models.skill_traveller.assignment import STAssignment
from apps.my_learning.config import AllBaseLearningTypeChoices, LearningStatusChoices
from apps.my_learning.models import BaseUserTrackingModel, UserCourseTracker
from apps.my_learning.models.tracker.assignment import AssignmentTracker
from apps.my_learning.models.tracker.skill_traveller.assessment import STAssessmentTracker


class UserSkillTravellerTracker(BaseUserTrackingModel):
    """User SkillTraveller Tracking Model for IIHT-B2B."""

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_user_skill_traveller_trackers"

    skill_traveller = models.ForeignKey(
        to="learning.SkillTraveller", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    def skill_traveller_progress_update(self):
        """Update the skill traveller progress based on the course progress."""

        courses = self.skill_traveller.related_skill_traveller_courses.all()
        course_trackers_progress_list = []
        for skill_traveller_course in courses:
            course_tracker = (
                skill_traveller_course.course.related_user_course_trackers.all().filter(user=self.user).first()
            )
            course_trackers_progress_list.append(course_tracker.progress if course_tracker else 0)

        skill_traveller_progress = (
            round(sum(course_trackers_progress_list) / len(course_trackers_progress_list))
            if course_trackers_progress_list
            else 0
        )
        if not self.is_completed:
            self.progress = skill_traveller_progress
            if skill_traveller_progress == 100:
                self.is_completed = True
                self.enrollment.learning_status = LearningStatusChoices.completed
                self.completion_date = timezone.now()
                self.enrollment.save()
        self.last_accessed_on = timezone.now()
        self.save()
        if not self.is_ccms_obj:
            self.user.related_skill_ontology_progress_update(
                learning_type=AllBaseLearningTypeChoices.skill_traveller, learning_obj=self.skill_traveller
            )

        return self

    def handle_skill_traveller_start(self):
        """Save the is_started is true when the skill_traveller is started."""

        self.is_started = True
        self.last_accessed_on = timezone.now()
        self.save()
        skill_traveller_courses = self.skill_traveller.related_skill_traveller_courses.all().order_by("sequence")
        for skill_traveller_course in skill_traveller_courses:
            course_tracking_kwargs = {
                "course": skill_traveller_course.course,
                "valid_till": skill_traveller_course.course.end_date,
                "created_by": self.created_by,
                "user": self.user,
            }
            UserCourseTracker.objects.get_or_create(**course_tracking_kwargs)

        self.skill_traveller_progress_update()
        return self

    @classmethod
    def report_data(cls, skill_traveller, user):
        """Function to return user st tracker details for report."""

        data = skill_traveller.report_data()
        data.update(**cls.get_default_report_data())
        st_tracker = cls.objects.filter(skill_traveller=skill_traveller, user=user).first()
        if not st_tracker:
            return data
        assessment_ids = STAssessment.objects.filter(
            Q(skill_traveller=skill_traveller) | Q(st_course__skill_traveller=skill_traveller)
        ).values_list("id", flat=True)
        assignment_ids = STAssignment.objects.filter(
            Q(skill_traveller=skill_traveller) | Q(st_course__skill_traveller=skill_traveller)
        ).values_list("assignment_id", flat=True)
        assessment_trackers_data = STAssessmentTracker.assessment_report_data(user, assessment_ids)
        assignment_trackers_data = AssignmentTracker.assignment_report_data(user, assignment_ids)
        data.update(
            {
                "video_progress": st_tracker.progress,
                "start_date": st_tracker.created_at,
                "completion_date": st_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if st_tracker.is_completed
                else LearningStatusChoices.in_progress,
                **assessment_trackers_data,
                **assignment_trackers_data,
            }
        )
        return data
