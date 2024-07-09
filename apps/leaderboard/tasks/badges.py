from apps.common.tasks import BaseAppTask
from apps.leaderboard.config import BadgeCategoryChoices, BadgeLearningTypeChoices
from apps.learning.config import AssessmentTypeChoices


class CommonBadgeTask(BaseAppTask):
    """Task to verify & include badges & points based on given user & type."""

    request_headers = None

    def run(self, db_name, category, learning_type, tracker_id, badge_type=None, **kwargs):
        """Run handler."""

        from apps.leaderboard.models import Badge
        from apps.learning.helpers import get_ccms_retrieve_details
        from apps.my_learning.models import CourseAssessmentTracker, CourseSubModuleTracker, LPAssessmentTracker

        assessment_tracker_models = {
            BadgeLearningTypeChoices.course: CourseAssessmentTracker,
            BadgeLearningTypeChoices.learning_path: LPAssessmentTracker,
        }
        self.switch_db(db_name)
        self.logger.info(f"Got Badges Task For : {db_name}.")

        self.request_headers = kwargs.get("request")

        match category:
            case BadgeCategoryChoices.video:
                tracker = CourseSubModuleTracker.objects.get(id=tracker_id)
                if getattr(tracker, "is_ccms_obj", False):
                    success, data = get_ccms_retrieve_details(
                        learning_type=learning_type,
                        instance_id=tracker.module_tracker.course_tracker.ccms_id,
                        request=self.request_headers,
                    )
                    if success:
                        proficiency = data["data"]["proficiency"]
                    else:
                        self.logger.info(f"Video badge creation failed because of {data}")
                        return False
                else:
                    proficiency = tracker.sub_module.module.course.proficiency
                if badge := Badge.objects.filter(category=category, type=badge_type, proficiency=proficiency).first():
                    return self.create_user_video_badge(badge=badge, learning_type=learning_type, tracker=tracker)
            case BadgeCategoryChoices.mml:
                # TODO: No data to track MML spent time of user. Need more clarity from IIHT Team.
                pass
            case BadgeCategoryChoices.assessment:
                # TODO: Need to add support for ccms assessments. @Teja @Sugadev
                assessment_tracker_model = assessment_tracker_models.get(learning_type)
                tracker = assessment_tracker_model.objects.get(id=tracker_id)
                if not tracker.progress:
                    return False
                assessment_instance = tracker.assessment
                assessment_data = {
                    "tracker": tracker.id,
                    "assessment_type": assessment_instance.type,
                    "parent_id": None,
                }
                proficiency = learning_id = user_id = None
                if assessment_instance.type == AssessmentTypeChoices.dependent_assessment:
                    if learning_type == BadgeLearningTypeChoices.course:
                        proficiency = assessment_instance.module.course.proficiency
                        user_id = tracker.module_tracker.course_tracker.user.id
                        learning_id = f"{assessment_instance.module.course.uuid}"
                        assessment_data["parent_id"] = assessment_instance.module.id
                    elif learning_type == BadgeLearningTypeChoices.learning_path:
                        proficiency = assessment_instance.lp_course.learning_path.proficiency
                        user_id = tracker.user
                        learning_id = f"{assessment_instance.lp_course.learning_path.uuid}"
                        assessment_data["parent_id"] = assessment_instance.lp_course.id
                elif assessment_instance.type == AssessmentTypeChoices.final_assessment:
                    if learning_type == BadgeLearningTypeChoices.course:
                        proficiency = assessment_instance.course.proficiency
                        user_id = tracker.course_tracker.user.id
                        learning_id = f"{assessment_instance.course.uuid}"
                        assessment_data["parent_id"] = assessment_instance.course.id
                    elif learning_type == BadgeLearningTypeChoices.learning_path:
                        proficiency = assessment_instance.learning_path.proficiency
                        user_id = tracker.user
                        learning_id = f"{assessment_instance.learning_path.uuid}"
                        assessment_data["parent_id"] = assessment_instance.learning_path.id
                badge = Badge.objects.filter(
                    to_range__gte=tracker.progress,
                    from_range__lte=tracker.progress,
                    category=category,
                    proficiency=proficiency,
                ).first()
                if badge:
                    return self.create_user_assessment_badge(
                        badge=badge,
                        learning_type=learning_type,
                        tracker=tracker,
                        user_id=user_id,
                        learning_id=learning_id,
                        assessment_data=assessment_data,
                    )
        return False

    @staticmethod
    def is_existing_badge(user_id, badge, learning_type, learning_id, tracker):
        """Find if existing badge available."""

        from apps.leaderboard.models import BadgeActivity

        if activity := BadgeActivity.objects.filter(
            user_id=user_id,
            badge__category=badge.category,
            badge__type=badge.type,
            learning_type=learning_type,
            learning_id=learning_id,
            tracker_id=f"{tracker.uuid}",
        ).first():
            return True, activity
        return False, None

    def create_user_assessment_badge(self, badge, learning_type, tracker, user_id, learning_id, assessment_data):
        """Creating Assessment badge."""

        from apps.leaderboard.models import BadgeActivity

        is_exists, activity = self.is_existing_badge(user_id, badge, learning_type, learning_id, tracker)
        if is_exists:
            self.logger.info(f"Updating assessment badge activity for user id: {user_id}")
            if activity.points < badge.points:
                activity.badge = badge
                activity.points = badge.points
                activity.data = assessment_data
                activity.save()
            self.logger.info(f"Assessment badge activity successfully updated for {activity.user}")
        else:
            self.logger.info(f"Adding assessment badge activity for user id: {user_id}")

            badge_activity = BadgeActivity.objects.create(
                user_id=user_id,
                badge=badge,
                learning_type=learning_type,
                learning_id=learning_id,
                points=badge.points,
                data=assessment_data,
                is_ccms_obj=getattr(tracker, "is_ccms_obj", False),
                tracker_id=f"{tracker.uuid}",
            )
            self.logger.info(f"Assessment badge activity successfully added for {badge_activity.user}")
        return True

    def create_user_video_badge(self, badge, learning_type, tracker):
        """Creating video badge."""

        from apps.leaderboard.models import BadgeActivity
        from apps.learning.config import SubModuleTypeChoices
        from apps.learning.models import CourseSubModule
        from apps.my_learning.helpers import get_ccms_list_details

        enrollment = tracker.module_tracker.course_tracker.enrollment
        user_id = tracker.module_tracker.course_tracker.user.id
        activity_data = {"enrollment_id": enrollment.id, "submodule_tracker_id": tracker.id}
        is_ccms_obj = getattr(tracker, "is_ccms_obj", False)
        if not is_ccms_obj:
            course = tracker.sub_module.module.course
            course_uuid = f"{course.uuid}"
            no_of_videos = CourseSubModule.objects.filter(
                module__course=course, type=SubModuleTypeChoices.video
            ).count()
        else:  # TODO: Need to implement ccms support here.
            course_uuid = f"{tracker.module_tracker.course_tracker.ccms_id}"
            success, data = get_ccms_list_details(
                learning_type="course_submodule",
                request=self.request_headers,
                params={"module__course__uuid": course_uuid, "type": SubModuleTypeChoices.video},
            )
            if success:
                no_of_videos = data["data"]["count"]
            else:
                self.logger.info(f"Video badge creation failed because of {data}")
                return False
        point_per_video = (badge.points / no_of_videos) if badge.points != 0 else 0

        if self.is_existing_badge(user_id, badge, learning_type, course_uuid, tracker)[0]:
            return False

        self.logger.info(f"Adding video badge activity for user id: {user_id}")
        badge_activity = BadgeActivity.objects.create(
            user_id=user_id,
            badge=badge,
            learning_type=learning_type,
            learning_id=course_uuid,
            points=point_per_video,
            data=activity_data,
            is_ccms_obj=is_ccms_obj,
            tracker_id=f"{tracker.uuid}",
        )
        self.logger.info(f"Video badge activity successfully added for {badge_activity.user}")
        return True
