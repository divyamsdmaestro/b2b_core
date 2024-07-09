from django.db.models import Sum
from django.utils import timezone

from apps.leaderboard.config import BadgeCategoryChoices, BadgeLearningTypeChoices, BadgeTypeChoices, MilestoneChoices
from apps.my_learning.config import AllBaseLearningTypeChoices, LearningStatusChoices
from apps.my_learning.tasks import BaseLearningEmailTask


class CourseProgressUpdateTask(BaseLearningEmailTask):
    """Task to update the progress for trackers."""

    # TODO: Need to handle this for CCMS courses lp & alp as well and validate the dependencies completed or not.

    request_headers = None

    def update_submodule_progress(self, instance, db_name):
        """Update the submodule progress."""

        from apps.leaderboard.tasks.badges import CommonBadgeTask
        from apps.learning.config import SubModuleTypeChoices
        from apps.learning.helpers import get_ccms_retrieve_details
        from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress
        from apps.tenant_service.middlewares import get_current_db_name

        if instance.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="course_submodule",
                instance_id=instance.ccms_id,
                request=self.request_headers,
                params={},
            )
            if success:
                data = data["data"]
                submodule_type = data["type"]["id"]
                duration = data["duration"]
            else:
                self.logger.info(f"Submodule progress update failed because of {data}")
                return False
        else:
            submodule_type = instance.sub_module.type
            duration = instance.sub_module.duration
        if submodule_type != SubModuleTypeChoices.video:
            instance.progress = 100
            instance.is_completed = True
            instance.completion_date = timezone.now()
        else:
            duration = duration
            completed = instance.completed_duration
            progress = round(((completed / duration) * 100), 2) if duration != 0 else 0
            if not instance.is_completed:
                instance.progress = get_actual_progress(instance.progress, progress)
                if progress == 100:
                    instance.is_completed = True
                    instance.completion_date = timezone.now()
                    CommonBadgeTask().run_task(
                        db_name=get_current_db_name(),
                        category=BadgeCategoryChoices.video,
                        badge_type=BadgeTypeChoices.video,
                        learning_type=BadgeLearningTypeChoices.course,
                        tracker_id=instance.id,
                        request=self.request_headers,
                    )
        instance.save()
        self.logger.info("SubModule progress updated successfully.")
        self.update_module_progress(instance.module_tracker, db_name)

    def update_module_progress(self, instance, db_name):
        """Update the module progress."""

        from apps.leaderboard.tasks import CommonLeaderboardTask
        from apps.my_learning.helpers import get_ccms_list_details
        from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress

        if instance.is_ccms_obj:
            success, data = get_ccms_list_details(
                learning_type="course_submodule",
                request=self.request_headers,
                params={"module__uuid": instance.ccms_id},
            )
            if success:
                no_of_submodule = data["data"]["count"]
            else:
                self.logger.info(f"Module progress update failed because of {data}")
                return False
            sub_module_tracker = instance.related_course_sub_module_trackers.all()
        else:
            no_of_submodule = instance.module.related_course_sub_modules.alive().count()
            sub_module_tracker = instance.related_course_sub_module_trackers.filter(sub_module__is_deleted=False)
        sub_module_tracker_percentage = sub_module_tracker.aggregate(Sum("progress"))["progress__sum"] or 0
        progress = 0
        if no_of_submodule != 0 and sub_module_tracker_percentage != 0:
            progress = round((sub_module_tracker_percentage / no_of_submodule), 2)
        if not instance.is_completed:
            instance.progress = get_actual_progress(instance.progress, progress)
            if progress == 100:
                instance.is_completed = True
                instance.completion_date = timezone.now()
                instance.save()
                if instance.is_ccms_obj:
                    extra_kwargs = {
                        "is_ccms_obj": instance.is_ccms_obj,
                        "ccms_id": instance.course_tracker.ccms_id,
                    }
                else:
                    extra_kwargs = {
                        "course_id": instance.course_tracker.course.id,
                    }
                CommonLeaderboardTask().run_task(
                    milestone_names=MilestoneChoices.module_completion_in_first_enrolled_course,
                    user_id=instance.course_tracker.user.id,
                    db_name=db_name,
                    learning_type=AllBaseLearningTypeChoices.course,
                    request=self.request_headers,
                    **extra_kwargs,
                )
        instance.save()
        self.logger.info("Module progress updated successfully.")
        self.update_course_progress(instance.course_tracker, db_name)

    def update_course_progress(self, course_tracker, db_name):
        """Update the course progress."""

        from apps.leaderboard.tasks import CommonLeaderboardTask
        from apps.mailcraft.config import MailTypeChoices
        from apps.my_learning.helpers import get_ccms_list_details
        from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress
        from apps.my_learning.tasks import LPProgressUpdateTask
        from apps.notification.config import NotifyActionChoices
        from apps.notification.models import Notification

        if course_tracker.is_ccms_obj:
            success, data = get_ccms_list_details(
                learning_type="course_module",
                request=self.request_headers,
                params={"course": str(course_tracker.ccms_id)},
            )
            if success:
                module_count = data["data"]["count"]
            else:
                self.logger.info(f"Course progress update failed because of {data}")
                return False
            module_trackers = course_tracker.related_course_module_trackers.all()
            course_name, course_id, is_ce = None, str(course_tracker.ccms_id), False
            # TODO: This is temporary solution. Need to fix this in proper way.
            if module_count > 0:
                try:
                    course_name = data["data"]["results"][0]["course"]["name"]
                    is_ce = data["data"]["results"][0]["course"]["is_certificate_enabled"]
                except:  # noqa
                    pass
            leaderboard_kwargs = {
                "is_ccms_obj": course_tracker.is_ccms_obj,
                "ccms_id": course_tracker.ccms_id,
            }
        else:
            module_count = course_tracker.course.related_course_modules.alive().count()
            module_trackers = course_tracker.related_course_module_trackers.filter(module__is_deleted=False)
            course_name, course_id = course_tracker.course.name, course_tracker.course.id
            is_ce = course_tracker.course.is_certificate_enabled
            leaderboard_kwargs = {
                "course_id": course_tracker.course.id,
            }
        module_tracker_percentage = module_trackers.aggregate(Sum("progress"))["progress__sum"] or 0
        progress = 0
        if module_tracker_percentage != 0 and module_count != 0:
            progress = round((module_tracker_percentage / module_count), 2)
        if not course_tracker.is_completed:
            course_tracker.progress = get_actual_progress(course_tracker.progress, progress)
            if progress == 100:
                course_tracker.is_completed = True
                course_tracker.enrollment.learning_status = LearningStatusChoices.completed
                course_tracker.enrollment.save()
                course_tracker.completion_date = timezone.now()
                course_tracker.save()
                milestone_names = [MilestoneChoices.first_course_complete, MilestoneChoices.course_completion]
                mail_types = [MailTypeChoices.course_completion]
                if is_ce:
                    milestone_names.append(MilestoneChoices.course_certificate_earned)
                    mail_types.append(MailTypeChoices.certification_mail)
                Notification.notify_user(
                    course_tracker.user, NotifyActionChoices.course_complete, obj_name=course_name, course_id=course_id
                )
                CommonLeaderboardTask().run_task(
                    milestone_names=milestone_names,
                    user_id=course_tracker.user.id,
                    db_name=db_name,
                    request=self.request_headers,
                    learning_type=AllBaseLearningTypeChoices.course,
                    **leaderboard_kwargs,
                )
                self.send_learning_email(
                    artifact_name=course_name,
                    user=course_tracker.user,
                    db_name=db_name,
                    completion_date=course_tracker.completion_date,
                    mail_types=mail_types,
                )
        course_tracker.last_accessed_on = timezone.now()
        course_tracker.save()
        self.logger.info("Course progress updated successfully.")
        LPProgressUpdateTask().run_task(
            db_name=db_name, course_tracker_id=course_tracker.id, request=self.request_headers
        )
        if not course_tracker.is_ccms_obj:
            course_tracker.user.related_skill_ontology_progress_update(
                AllBaseLearningTypeChoices.course, course_tracker.course, db_name
            )
        return True

    def run(self, db_name, tracker, **kwargs):
        """Run handler."""

        from apps.my_learning.models import CourseSubModuleTracker

        self.switch_db(db_name=db_name)
        self.request_headers = kwargs.get("request")
        self.logger.info("*** Updating progress for submodules & related learnings.***")
        try:
            submodule_tracker = CourseSubModuleTracker.objects.get(pk=tracker)
            self.update_submodule_progress(submodule_tracker, db_name)
            return True
        except:  # noqa
            return False
