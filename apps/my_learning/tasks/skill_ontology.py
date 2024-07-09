from django.db.models import Sum
from django.utils import timezone

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import AllBaseLearningTypeChoices, LearningStatusChoices
from apps.notification.config import NotifyActionChoices


class SkillOntologyProgressUpdateTask(BaseAppTask):
    """Task to update the progress for skill ontology trackers."""

    def calculate_overall_progress(self, user, **kwargs):
        """Function to calculate the overall progress."""

        from apps.my_learning.serializers.v1 import tracker_related_fields

        overall_progress = 0
        learnings_count = 0
        for learning_type, learning_objs in kwargs.items():
            filter_params = {f"{learning_type}__in": learning_objs}
            overall_progress += (
                getattr(user, tracker_related_fields[learning_type])
                .filter(**filter_params)
                .aggregate(Sum("progress"))["progress__sum"]
                or 0
            )
            learnings_count += learning_objs.count()
        skill_ontology_progress = (
            round(overall_progress / learnings_count) if learnings_count > 0 and overall_progress > 0 else 0
        )
        return skill_ontology_progress

    def skill_ontology_progress_update(self, tracker):
        """Update the skill ontology progress based on the all the related learnings progress."""

        from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress
        from apps.notification.models import Notification

        if not tracker.is_completed:
            user = tracker.user
            skill_ontology = tracker.skill_ontology
            overall_progress = self.calculate_overall_progress(
                user,
                **{
                    AllBaseLearningTypeChoices.course: skill_ontology.course.all(),
                    AllBaseLearningTypeChoices.learning_path: skill_ontology.learning_path.all(),
                    AllBaseLearningTypeChoices.advanced_learning_path: skill_ontology.advanced_learning_path.all(),
                    AllBaseLearningTypeChoices.skill_traveller: skill_ontology.skill_traveller.all(),
                    AllBaseLearningTypeChoices.assignment: skill_ontology.assignment.all(),
                    AllBaseLearningTypeChoices.assignment_group: skill_ontology.assignment_group.all(),
                },
            )
            tracker.progress = get_actual_progress(tracker.progress, overall_progress)
            if overall_progress == 100:
                tracker.is_completed = True
                tracker.enrollment.learning_status = LearningStatusChoices.completed
                tracker.completion_date = timezone.now()
                tracker.enrollment.save()
                Notification.notify_user(
                    tracker.user,
                    NotifyActionChoices.skill_ontology_complete,
                    obj_name=tracker.skill_ontology.name,
                    skill_ontology_id=tracker.skill_ontology.id,
                )
        tracker.last_accessed_on = timezone.now()
        tracker.save()

        return tracker

    def run(self, db_name, tracker_ids, **kwargs):
        """Run handler."""

        from apps.my_learning.models import UserSkillOntologyTracker

        self.switch_db(db_name=db_name)
        self.logger.info("*** Updating progress for skill ontology related learnings.***")

        trackers = UserSkillOntologyTracker.objects.filter(id__in=tracker_ids)
        for tracker in trackers:
            try:
                self.skill_ontology_progress_update(tracker)
            except Exception:
                pass
        return True
