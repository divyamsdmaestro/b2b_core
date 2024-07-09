from django.utils import timezone

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import LearningStatusChoices


class PlaygroundGroupEnrollmentTask(BaseAppTask):
    """Task to Enroll User to Playground Group and associated playgrounds."""

    def run(self, tracker_id, db_name, **kwargs):
        """Run handler."""

        from apps.my_learning.models.tracker.playground import UserPlaygroundTracker
        from apps.my_learning.models.tracker.playground_group import UserPlaygroundGroupTracker

        self.switch_db(db_name)
        self.logger.info("Executing PlaygroundGroupEnrollmentTask")

        tracker: UserPlaygroundGroupTracker = UserPlaygroundGroupTracker.objects.get(id=tracker_id)
        playground_relations = tracker.playground_group.related_playground_relations.all().order_by("sequence")
        for playground_relation in playground_relations:
            try:
                UserPlaygroundTracker.objects.get(playground=playground_relation.playground, user=tracker.user)
            except UserPlaygroundTracker.DoesNotExist:
                UserPlaygroundTracker.objects.create(
                    playground=playground_relation.playground,
                    user=tracker.user,
                )
        return True


class PlaygroundGroupTrackingTask(BaseAppTask):
    """Update the playground group progress based on the playground progress."""

    def run(self, tracker_id, db_name, **kwargs):
        """Run handler."""

        from apps.my_learning.models.tracker.playground_group import UserPlaygroundGroupTracker

        self.switch_db(db_name)
        self.logger.info("Executing PlaygroundGroupTrackingTask")

        tracker: UserPlaygroundGroupTracker = UserPlaygroundGroupTracker.objects.get(id=tracker_id)

        try:
            user_playground_trackers = tracker.user.related_user_playground_trackers.filter(
                playground__related_playground_relations__playground_group=tracker.playground_group
            )
        except Exception:
            user_playground_trackers = 0
        if not user_playground_trackers.exists():
            tracker.progress = 0
            tracker.save()
            return True
        total_playground_progress = list(user_playground_trackers.values_list("progress", flat=True))
        playground_group_progress = round(sum(total_playground_progress) / len(total_playground_progress))
        tracker.progress = playground_group_progress
        if playground_group_progress == 100:
            tracker.is_completed = True
            tracker.enrollment.learning_status = LearningStatusChoices.completed
            tracker.completion_date = timezone.now()
            tracker.enrollment.save()
        tracker.last_accessed_on = timezone.now()
        tracker.save()
