from django.db.models import Sum
from django.utils import timezone

from apps.my_learning.tasks import BaseLearningEmailTask


class ALPProgressUpdateTask(BaseLearningEmailTask):
    """Task to update the progress for learning path trackers."""

    request_headers = None

    def run(self, db_name, lp_tracker_id=None, alp_tracker_id=None, **kwargs):
        """Run handler."""

        from apps.my_learning.helpers import get_ccms_list_details
        from apps.my_learning.models import UserALPTracker, UserLearningPathTracker

        self.switch_db(db_name=db_name)
        self.logger.info("*** Updating progress for advanced_learning_paths & related learnings.***")

        self.request_headers = kwargs.get("request", None)

        if lp_tracker_id:
            lp_tracker = UserLearningPathTracker.objects.get(id=lp_tracker_id)
            user = lp_tracker.user
            if lp_tracker.is_ccms_obj:
                success, data = get_ccms_list_details(
                    learning_type="alp_core_lp",
                    request=self.request_headers,
                    params={"learning_path": str(lp_tracker.ccms_id)},
                )
                if success:
                    for alp in data["data"] or {}:
                        if alp_tracker := user.related_user_alp_trackers.filter(
                            ccms_id=alp, is_completed=False
                        ).first():
                            alp_lp_count = len(data["data"][alp]["learning_paths"] or [])
                            alp_lps = data["data"][alp]["learning_paths"]
                            alp_name = data["data"][alp]["alp_data"]["name"]
                            is_ce = data["data"][alp]["alp_data"]["is_certificate_enabled"]
                            alp_progress = self.get_ccms_alp_progress(user=user, lps=alp_lps, count=alp_lp_count)
                            self.update_alp_progress(
                                alp_tracker=alp_tracker,
                                user=alp_tracker.user,
                                progress=alp_progress,
                                alp_name=alp_name,
                                is_ce=is_ce,
                                db_name=db_name,
                            )
                    return True
                else:
                    self.logger.info(f"***ALP progress update failed because of {data}.****")
                    return False
            else:
                alp_ids = (
                    lp_tracker.learning_path.related_alp_learning_paths.filter(
                        advanced_learning_path__is_deleted=False
                    )
                    .values_list("advanced_learning_path", flat=True)
                    .distinct()
                )
                for alp_id in alp_ids:
                    if alp_tracker := user.related_user_alp_trackers.filter(
                        advanced_learning_path=alp_id, is_completed=False
                    ).first():
                        alp_progress = self.get_core_alp_progress(user=user, alp_tracker=alp_tracker)
                        self.update_alp_progress(
                            alp_tracker=alp_tracker,
                            user=user,
                            progress=alp_progress,
                            alp_name=alp_tracker.advanced_learning_path.name,
                            is_ce=alp_tracker.advanced_learning_path.is_certificate_enabled,
                            db_name=db_name,
                        )
                return True
        elif alp_tracker_id:
            if alp_tracker := UserALPTracker.objects.filter(id=alp_tracker_id, is_completed=False).first():
                user = alp_tracker.user
                if alp_tracker.is_ccms_obj:
                    success, data = get_ccms_list_details(
                        learning_type="alp_lp",
                        request=self.request_headers,
                        params={"advanced_learning_path__uuid": str(alp_tracker.ccms_id)},
                    )
                    if not success:
                        self.logger.info(f"***ALP progress update failed because of {data}.****")
                        return False
                    alp_lp_count = data["data"]["count"]
                    alp_lps = data["data"]["results"]
                    alp_name = None
                    is_ce = False
                    if alp_lp_count > 0:
                        alp_name = data["data"]["results"][0]["advanced_learning_path"]["name"]
                        is_ce = data["data"]["results"][0]["advanced_learning_path"]["is_certificate_enabled"]
                    lp_id = []
                    for lp in alp_lps:
                        lp_id.append(lp["learning_path"]["uuid"])
                    alp_progress = self.get_ccms_alp_progress(user=user, lps=lp_id, count=alp_lp_count)
                else:
                    alp_progress = self.get_core_alp_progress(user=user, alp_tracker=alp_tracker)
                    alp_name = alp_tracker.advanced_learning_path.name
                    is_ce = alp_tracker.advanced_learning_path.is_certificate_enabled
                self.update_alp_progress(
                    alp_tracker=alp_tracker,
                    user=user,
                    progress=alp_progress,
                    alp_name=alp_name,
                    is_ce=is_ce,
                    db_name=db_name,
                )
                return True
            return False
        else:
            return False

    def update_alp_progress(self, alp_tracker, user, progress, alp_name, is_ce, db_name):
        """Updating ALP progress for tenant level ALP's."""

        from apps.leaderboard.config import MilestoneChoices
        from apps.leaderboard.tasks import CommonLeaderboardTask
        from apps.mailcraft.config import MailTypeChoices
        from apps.my_learning.config import AllBaseLearningTypeChoices
        from apps.my_learning.models.tracker.tracker_helpers import get_actual_progress
        from apps.notification.config import NotifyActionChoices
        from apps.notification.models import Notification

        alp_tracker.progress = get_actual_progress(alp_tracker.progress, progress)
        if progress >= 100:
            alp_tracker.is_completed = True
            alp_tracker.completion_date = alp_tracker.last_accessed_on = timezone.now()
            alp_tracker.save()
            if alp_tracker.is_ccms_obj:
                alp_id = str(alp_tracker.ccms_id)
                extra_kwargs = {
                    "is_ccms_obj": True,
                    "ccms_id": alp_id,
                }
            else:
                alp_id = alp_tracker.advanced_learning_path.id
                extra_kwargs = {
                    "advanced_learning_path_id": alp_id,
                }
            Notification.notify_user(
                alp_tracker.user,
                NotifyActionChoices.alp_complete,
                obj_name=alp_name,
                advanced_learning_path_id=alp_id,
            )
            milestone_names = [
                MilestoneChoices.first_certification_path_completion,
                MilestoneChoices.certification_path_completion,
            ]
            mail_types = [MailTypeChoices.alp_completion]
            if is_ce:
                milestone_names.append(MilestoneChoices.certification_path_certificate_earned)
                mail_types.append(MailTypeChoices.certification_mail)
            CommonLeaderboardTask().run_task(
                milestone_names=milestone_names,
                user_id=user.id,
                db_name=db_name,
                learning_type=AllBaseLearningTypeChoices.advanced_learning_path,
                **extra_kwargs,
            )
            self.send_learning_email(
                artifact_name=alp_name,
                user=user,
                db_name=db_name,
                completion_date=alp_tracker.completion_date,
                mail_types=mail_types,
            )
        alp_tracker.last_accessed_on = timezone.now()
        alp_tracker.save()
        self.logger.info("""ALP progress updated successfully.""")
        if not alp_tracker.is_ccms_obj:
            user.related_skill_ontology_progress_update(
                AllBaseLearningTypeChoices.advanced_learning_path, alp_tracker.advanced_learning_path, db_name
            )

    @staticmethod
    def get_ccms_alp_progress(user, lps, count):
        """Returns the overall progress of ccms alp."""

        alp_lp_progress = (
            user.related_user_learning_path_trackers.filter(ccms_id__in=lps).aggregate(Sum("progress"))[
                "progress__sum"
            ]
            or 0
        )
        overall_progress = round(alp_lp_progress / count) if count > 0 else 0
        return overall_progress

    @staticmethod
    def get_core_alp_progress(user, alp_tracker):
        """Returns the overall progress of core alp."""

        alp_lp = alp_tracker.advanced_learning_path.related_alp_learning_paths.filter(
            learning_path__is_deleted=False
        ).values_list("learning_path", flat=True)
        alp_lp_count = len(alp_lp)
        alp_lp_progress = (
            user.related_user_learning_path_trackers.filter(learning_path_id__in=alp_lp).aggregate(Sum("progress"))[
                "progress__sum"
            ]
            or 0
        )
        progress = round(alp_lp_progress / alp_lp_count) if alp_lp_count else 0
        return progress
