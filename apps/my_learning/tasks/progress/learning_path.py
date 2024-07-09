from django.db.models import Sum
from django.utils import timezone

from apps.my_learning.tasks import BaseLearningEmailTask


class LPProgressUpdateTask(BaseLearningEmailTask):
    """Task to update the progress for learning path trackers."""

    request_headers = None

    def run(self, db_name, course_tracker_id=None, lp_tracker_id=None, **kwargs):
        """Run handler."""

        from apps.my_learning.helpers import get_ccms_list_details
        from apps.my_learning.models import UserCourseTracker, UserLearningPathTracker

        self.switch_db(db_name=db_name)
        self.logger.info("*** Updating progress for learning_paths & related learnings.***")

        self.request_headers = kwargs.get("request", None)

        if course_tracker_id:
            course_tracker = UserCourseTracker.objects.get(id=course_tracker_id)
            user = course_tracker.user
            if course_tracker.is_ccms_obj:
                success, data = get_ccms_list_details(
                    learning_type="lp_core_course",
                    request=self.request_headers,
                    params={"course": str(course_tracker.ccms_id)},
                )
                if success:
                    for lp in data["data"] or {}:
                        if lp_tracker := user.related_user_learning_path_trackers.filter(
                            ccms_id=lp, is_completed=False
                        ).first():
                            lp_course_count = len(data["data"][lp]["courses"] or [])
                            lp_courses = data["data"][lp]["courses"]
                            lp_name = data["data"][lp]["lp_data"]["name"]
                            is_ce = data["data"][lp]["lp_data"]["is_certificate_enabled"]
                            lp_progress = self.get_ccms_lp_progress(
                                user=user, courses=lp_courses, count=lp_course_count
                            )
                            self.update_lp_progress(
                                lp_tracker=lp_tracker,
                                user=user,
                                db_name=db_name,
                                progress=lp_progress,
                                lp_name=lp_name,
                                is_ce=is_ce,
                            )
                    return True
                else:
                    self.logger.info(f"***LP progress update failed because of {data}.****")
                    return False
            else:
                # update the learning_path progress based on course progress.
                # TODO: Need to implement the leaderboard, badges tasks & Need to remove the skill_traveller from here.
                lp_ids = (
                    course_tracker.course.related_learning_path_courses.filter(learning_path__is_deleted=False)
                    .values_list("learning_path", flat=True)
                    .distinct()
                )
                skill_traveller_courses = course_tracker.course.related_skill_traveller_courses.all()
                for lp_id in lp_ids:
                    if lp_tracker := user.related_user_learning_path_trackers.filter(
                        learning_path=lp_id, is_completed=False
                    ).first():
                        lp_progress = self.get_core_lp_progress(user=user, lp_tracker=lp_tracker)
                        self.update_lp_progress(
                            lp_tracker=lp_tracker,
                            user=user,
                            db_name=db_name,
                            progress=lp_progress,
                            lp_name=lp_tracker.learning_path.name,
                            is_ce=lp_tracker.learning_path.is_certificate_enabled,
                        )
                for course in skill_traveller_courses:
                    if st_tracker := course.skill_traveller.related_user_skill_traveller_trackers.filter(
                        user=course_tracker.user
                    ).first():
                        st_tracker.skill_traveller_progress_update()
                return True
        elif lp_tracker_id:
            if lp_tracker := UserLearningPathTracker.objects.filter(id=lp_tracker_id, is_completed=False).first():
                user = lp_tracker.user
                if lp_tracker.is_ccms_obj:
                    success, data = get_ccms_list_details(
                        learning_type="lp_course",
                        request=self.request_headers,
                        params={"learning_path__uuid": str(lp_tracker.ccms_id)},
                    )
                    if not success:
                        self.logger.info(f"***LP progress update failed because of {data}.****")
                        return False
                    lp_course_count = data["data"]["count"]
                    lp_courses = data["data"]["results"]
                    lp_name = None
                    is_ce = False
                    if lp_course_count > 0:
                        lp_name = data["data"]["results"][0]["learning_path"]["name"]
                        is_ce = data["data"]["results"][0]["learning_path"]["is_certificate_enabled"]
                    course_id = []
                    for lp_course in lp_courses:
                        course_id.append(lp_course["course"]["uuid"])
                    lp_progress = self.get_ccms_lp_progress(user=user, courses=course_id, count=lp_course_count)
                else:
                    lp_progress = self.get_core_lp_progress(user=user, lp_tracker=lp_tracker)
                    lp_name = lp_tracker.learning_path.name
                    is_ce = lp_tracker.learning_path.is_certificate_enabled
                self.update_lp_progress(
                    lp_tracker=lp_tracker,
                    user=user,
                    db_name=db_name,
                    progress=lp_progress,
                    lp_name=lp_name,
                    is_ce=is_ce,
                )
                return True
            return False
        else:
            return False

    def update_lp_progress(self, lp_tracker, user, db_name, progress, lp_name, is_ce):
        """Updating LP progress for tenant level LP's."""

        from apps.leaderboard.config import MilestoneChoices
        from apps.leaderboard.tasks import CommonLeaderboardTask
        from apps.mailcraft.config import MailTypeChoices
        from apps.my_learning.config import AllBaseLearningTypeChoices
        from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress
        from apps.my_learning.tasks import ALPProgressUpdateTask
        from apps.notification.config import NotifyActionChoices
        from apps.notification.models import Notification

        lp_tracker.progress = get_actual_progress(lp_tracker.progress, progress)
        if progress >= 100:
            lp_tracker.is_completed = True
            lp_tracker.completion_date = lp_tracker.last_accessed_on = timezone.now()
            lp_tracker.save()
            if lp_tracker.is_ccms_obj:
                lp_id = str(lp_tracker.ccms_id)
                extra_kwargs = {
                    "is_ccms_obj": True,
                    "ccms_id": lp_id,
                }
            else:
                lp_id = lp_tracker.learning_path.id
                extra_kwargs = {
                    "learning_path_id": lp_id,
                }
            Notification.notify_user(
                lp_tracker.user,
                NotifyActionChoices.lp_complete,
                obj_name=lp_name,
                learning_path_id=lp_id,
            )
            milestone_names = [
                MilestoneChoices.first_learning_path_complete,
                MilestoneChoices.learning_path_completion,
            ]
            mail_types = [MailTypeChoices.lp_completion]
            if is_ce:
                milestone_names.append(MilestoneChoices.learning_path_certificate_earned)
                mail_types.append(MailTypeChoices.certification_mail)
            CommonLeaderboardTask().run_task(
                milestone_names=milestone_names,
                user_id=user.id,
                db_name=db_name,
                learning_type=AllBaseLearningTypeChoices.learning_path,
                **extra_kwargs,
            )
            self.send_learning_email(
                artifact_name=lp_name,
                user=user,
                db_name=db_name,
                completion_date=lp_tracker.completion_date,
                mail_types=mail_types,
            )
        lp_tracker.last_accessed_on = timezone.now()
        lp_tracker.save()
        ALPProgressUpdateTask().run_task(db_name=db_name, lp_tracker_id=lp_tracker.id, request=self.request_headers)
        self.logger.info("""LP progress updated successfully.""")
        if not lp_tracker.is_ccms_obj:
            user.related_skill_ontology_progress_update(
                AllBaseLearningTypeChoices.learning_path, lp_tracker.learning_path, db_name
            )
        return True

    @staticmethod
    def get_ccms_lp_progress(user, courses, count):
        """Returns the overall progress of ccms lp."""

        lp_course_progress = (
            user.related_user_course_trackers.filter(ccms_id__in=courses).aggregate(Sum("progress"))["progress__sum"]
            or 0
        )
        overall_progress = round(lp_course_progress / count) if count > 0 else 0
        return overall_progress

    @staticmethod
    def get_core_lp_progress(user, lp_tracker):
        """Returns the overall progress of core lp."""

        lp_courses = lp_tracker.learning_path.related_learning_path_courses.filter(
            course__is_deleted=False
        ).values_list("course", flat=True)
        lp_course_count = len(lp_courses)
        lp_course_progress = (
            user.related_user_course_trackers.filter(course_id__in=lp_courses).aggregate(Sum("progress"))[
                "progress__sum"
            ]
            or 0
        )
        progress = round(lp_course_progress / lp_course_count) if lp_course_count else 0
        return progress
