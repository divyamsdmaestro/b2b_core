from django.utils import timezone

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import LearningStatusChoices


class PlaygroundTrackingTask(BaseAppTask):
    """Task to update playground activity and progress."""

    def run(self, tracker_id, db_name, **kwargs):
        """Run handler."""

        from apps.my_learning.models.tracker.playground import UserPlaygroundTracker
        from apps.my_learning.tasks import PlaygroundGroupTrackingTask

        self.switch_db(db_name)
        self.logger.info("Executing PlaygroundTrackingTask")

        tracker: UserPlaygroundTracker = UserPlaygroundTracker.objects.get(id=tracker_id)
        tracker.progress = 100
        tracker.is_completed = True
        tracker.enrollment.learning_status = LearningStatusChoices.completed
        tracker.completion_date = timezone.now()
        tracker.enrollment.save()
        tracker.save()
        # update the playground_group progress based on playground progress.
        if group_trackers := tracker.user.related_user_playground_group_trackers.filter(
            playground_group__related_playground_relations__playground=tracker.playground
        ):
            for group_tracker in group_trackers:
                PlaygroundGroupTrackingTask().run_task(tracker_id=group_tracker.id, db_name=db_name)
        return True
