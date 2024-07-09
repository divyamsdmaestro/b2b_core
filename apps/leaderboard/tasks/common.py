from apps.common.tasks import BaseAppTask
from apps.leaderboard.config import MilestoneChoices
from apps.my_learning.config import MilestoneCategoryTypeChoices
from apps.tenant_service.middlewares import get_current_db_name


class CommonLeaderboardTask(BaseAppTask):
    """Task to verify & include leaderboard points based on given milestone."""

    lb_activity_klass = milestone = user = obj_klass = None
    conditional_choices_list = completion_milestone = request_headers = None

    def run(self, milestone_names, user_id, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User
        from apps.leaderboard.models import LeaderboardActivity, Milestone

        self.switch_db(db_name)
        self.logger.info(f"Got Leaderboard Task For : {milestone_names} on {get_current_db_name()}.")
        self.lb_activity_klass = LeaderboardActivity
        self.user = User.objects.get(id=user_id)
        self.request_headers = kwargs.get("request", None)
        if isinstance(milestone_names, str):
            milestone_names = [milestone_names]
        for milestone_choice in milestone_names:
            self.milestone = None
            try:
                self.milestone = Milestone.objects.active().get(
                    name=MilestoneChoices.get_choice(milestone_choice).value
                )
            except Milestone.DoesNotExist:
                continue
            match MilestoneChoices.get_milestone_category(self.milestone.name):
                case MilestoneCategoryTypeChoices.course:
                    self.handle_course_activity(**kwargs)
                case MilestoneCategoryTypeChoices.learning_path:
                    self.handle_lp_activity(**kwargs)
                case MilestoneCategoryTypeChoices.advanced_learning_path:
                    self.handle_alp_activity(**kwargs)
                case MilestoneCategoryTypeChoices.assessment:
                    self.handle_assessment_activity(**kwargs)
                case MilestoneCategoryTypeChoices.forum:
                    if not (
                        self.lb_activity_klass.objects.filter(
                            user=self.user, milestone=self.milestone, forum_id=kwargs.get("forum_id")
                        ).count()
                        >= 50
                    ):
                        self.handle_forum_activity(**kwargs)
                case _:
                    self.handle_activity(**kwargs)
        return True

    def handle_activity(self, **kwargs):
        """Handle normal lb activity flow."""

        activity, is_created = self.lb_activity_klass.find_or_create(user=self.user, milestone=self.milestone)
        if is_created:
            if kwargs.get("course_id"):
                activity.course_id = kwargs.get("course_id")
            if kwargs.get("learning_path_id"):
                activity.learning_path_id = kwargs.get("learning_path_id")
            if kwargs.get("is_ccms_obj"):
                activity.ccms_id = kwargs.get("ccms_id")
                activity.learning_type = kwargs.get("learning_type")
                activity.is_ccms_obj = True
            activity.points = self.milestone.points
            activity.save()
        return True

    def handle_course_activity(self, **kwargs):
        """Handle course related leaderboard activity."""

        from apps.learning.models import Course

        self.conditional_choices_list = self.completion_milestone = self.obj_klass = None
        self.conditional_choices_list = [
            MilestoneChoices.course_self_enroll,
            MilestoneChoices.course_assigned,
            MilestoneChoices.course_completion,
        ]
        self.completion_milestone = MilestoneChoices.course_completion
        if not kwargs.get("is_ccms_obj"):
            self.obj_klass = Course
        self.handle_learning_activity(**kwargs)
        return True

    def handle_lp_activity(self, **kwargs):
        """Handle course related leaderboard activity."""

        from apps.learning.models import LearningPath

        self.conditional_choices_list = self.completion_milestone = self.obj_klass = None
        self.conditional_choices_list = [
            MilestoneChoices.learning_path_self_enroll,
            MilestoneChoices.learning_path_assigned,
            MilestoneChoices.learning_path_completion,
        ]
        self.completion_milestone = MilestoneChoices.learning_path_completion
        if not kwargs.get("is_ccms_obj"):
            self.obj_klass = LearningPath
        self.handle_learning_activity(**kwargs)
        return True

    def handle_alp_activity(self, **kwargs):
        """Handle course related leaderboard activity."""

        from apps.learning.models import AdvancedLearningPath

        self.conditional_choices_list = self.completion_milestone = self.obj_klass = None
        self.conditional_choices_list = [
            MilestoneChoices.certification_path_self_enrolled,
            MilestoneChoices.certification_path_assigned,
            MilestoneChoices.certification_path_completion,
        ]
        self.completion_milestone = MilestoneChoices.certification_path_completion
        if not kwargs.get("is_ccms_obj"):
            self.obj_klass = AdvancedLearningPath
        self.handle_learning_activity(**kwargs)
        return True

    def handle_learning_activity(self, **kwargs):
        """Currently support Course, LearningPath & AdvancedLearningPath models. Just a DRY function."""

        from apps.learning.helpers import get_ccms_retrieve_details

        is_ccms_obj = kwargs.get("is_ccms_obj", False)
        learning_type = kwargs.get("learning_type")
        if is_ccms_obj:
            obj_id = kwargs.get("ccms_id")
            extra_kwargs = {
                "ccms_id": obj_id,
                "is_ccms_obj": is_ccms_obj,
                "learning_type": learning_type,
            }
        else:
            fk_id_key = learning_type + "_id"
            obj_id = kwargs.get(fk_id_key)
            extra_kwargs = {fk_id_key: obj_id}
        if self.milestone.name in self.conditional_choices_list:
            activity, is_created = self.lb_activity_klass.find_or_create(
                user=self.user, milestone=self.milestone, use_kwargs=True, **extra_kwargs
            )
        else:
            activity, is_created = self.lb_activity_klass.find_or_create(user=self.user, milestone=self.milestone)
        if is_created:
            activity_points = self.milestone.points
            if not is_ccms_obj and obj_id and not getattr(activity, fk_id_key):
                setattr(activity, fk_id_key, obj_id)
            elif is_ccms_obj and kwargs.get("ccms_id") and not getattr(activity, "ccms_id"):
                activity.ccms_id = obj_id
                activity.is_ccms_obj = is_ccms_obj
                activity.learning_type = learning_type
            if self.milestone.name == self.completion_milestone:
                if is_ccms_obj:
                    success, data = get_ccms_retrieve_details(
                        learning_type=learning_type,
                        instance_id=obj_id,
                        request=self.request_headers,
                    )
                    if success:
                        activity_points = data["data"]["learning_points"] or 0
                else:
                    activity_points = self.obj_klass.objects.get(id=obj_id).learning_points
            activity.points = activity_points
            activity.save()
        return True

    def handle_assessment_activity(self, **kwargs):
        """Handle Assessment Related Leaderboard Activities"""

        activity = self.lb_activity_klass.objects.create(user=self.user, milestone=self.milestone)
        if kwargs.get("course_id"):
            activity.course_id = kwargs.get("course_id")
        if kwargs.get("learning_path_id"):
            activity.learning_path_id = kwargs.get("learning_path_id")
        if kwargs.get("is_ccms_obj"):
            activity.ccms_id = kwargs.get("ccms_id")
            activity.learning_type = kwargs.get("learning_type")
            activity.is_ccms_obj = True
        activity.points = self.milestone.points
        activity.save()
        return True

    def handle_forum_activity(self, **kwargs):
        """Handle Forum Related Leaderboard Activities"""

        activity = self.lb_activity_klass.objects.create(
            user=self.user, milestone=self.milestone, forum_id=kwargs.get("forum_id")
        )
        activity.points = self.milestone.points
        activity.save()
        return True
