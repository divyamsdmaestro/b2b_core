from django.core.validators import MaxValueValidator
from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.common.models.base import CreationAndModificationModel
from apps.my_learning.config import LearningStatusChoices


class UserSkillOntologyTracker(CreationAndModificationModel):
    """User SkillOntology Tracking Model for IIHT-B2B."""

    class Meta(CreationAndModificationModel.Meta):
        default_related_name = "related_user_skill_ontology_trackers"

    skill_ontology = models.ForeignKey(
        to="learning.SkillOntology", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    enrollment = models.ForeignKey(
        to="my_learning.Enrollment", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    user = models.ForeignKey(to="access.User", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    last_accessed_on = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    completed_duration = models.PositiveIntegerField(default=0)
    progress = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    @classmethod
    def report_data(cls, skill_ontology, user):
        """Function to return user skill ontology tracker details for report."""

        data = skill_ontology.report_data()
        data.update(
            {
                "video_progress": None,
                "start_date": None,
                "completion_date": None,
                "learning_status": LearningStatusChoices.not_started,
            }
        )
        so_tracker = cls.objects.filter(skill_ontology=skill_ontology, user=user).first()
        if not so_tracker:
            return data
        data.update(
            {
                "video_progress": so_tracker.progress,
                "start_date": so_tracker.created_at,
                "completion_date": so_tracker.completion_date,
                "learning_status": LearningStatusChoices.completed
                if so_tracker.is_completed
                else LearningStatusChoices.in_progress,
            }
        )
        return data
