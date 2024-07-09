from apps.access_control.config import RoleTypeChoices
from apps.common.tasks import BaseAppTask
from apps.event.config import ActivityTypeChoices, CalendarEventTypeChoices


class CalendarActivityCreationTask(BaseAppTask):
    """Task to create event for the enrolled learnings by user."""

    def _create_event_for_alp(self, users, event_type, event_instance_id):
        """Create a new calendar event for the specified Advanced Learning Path."""

        from apps.learning.models import AdvancedLearningPath, LearningPath

        advanced_learning_path = AdvancedLearningPath.objects.filter(id=event_instance_id).first()
        if advanced_learning_path:
            learning_paths = LearningPath.objects.filter(
                related_alp_learning_paths__advanced_learning_path=advanced_learning_path
            )
            for user in users:
                if advanced_learning_path.start_date:
                    activity_data = {
                        "name": advanced_learning_path.name,
                        "description": advanced_learning_path.description,
                        "activity_type": ActivityTypeChoices.event,
                        "event_subtype": event_type,
                        "event_subtype_id": event_instance_id,
                        "activity_date": advanced_learning_path.start_date,
                        "ends_on": advanced_learning_path.end_date,
                    }
                    user.related_calendar_activities.get_or_create(**activity_data)
            if learning_paths:
                self._create_event_for_lp(users, learning_paths=learning_paths, alp_id=advanced_learning_path.id)
        return True

    def _create_event_for_lp(self, users, event_type=None, event_instance_id=None, learning_paths=[], alp_id=None):
        """Create a new calendar event for the specified Learning Path."""

        from apps.learning.models import LearningPath

        if not learning_paths and event_type == CalendarEventTypeChoices.learning_path:
            learning_paths = LearningPath.objects.filter(id=event_instance_id)
        for learning_path in learning_paths:
            for user in users:
                if learning_path.start_date:
                    activity_data = {
                        "name": learning_path.name,
                        "description": learning_path.description,
                        "activity_type": ActivityTypeChoices.event,
                        "activity_date": learning_path.start_date,
                        "ends_on": learning_path.end_date,
                    }
                    if alp_id:
                        activity_data.update(
                            {
                                "event_subtype": CalendarEventTypeChoices.alp_learning_path,
                                "event_subtype_id": alp_id,
                            }
                        )
                    else:
                        activity_data.update(
                            {
                                "event_subtype": CalendarEventTypeChoices.learning_path,
                                "event_subtype_id": learning_path.id,
                            }
                        )
                    user.related_calendar_activities.get_or_create(**activity_data)
        return True

    def _create_event_for_course(self, users, event_type=None, event_instance_id=None, courses=[]):
        """Create a new calendar event for the specified course."""

        from apps.learning.models import Course

        if not courses and event_type == CalendarEventTypeChoices.course:
            courses = Course.objects.filter(id=event_instance_id)
        for course in courses:
            course_modules = course.related_course_modules.filter(start_date__isnull=False)
            for user in users:
                if course.start_date:
                    activity_data = {
                        "name": course.name,
                        "description": course.description,
                        "activity_type": ActivityTypeChoices.event,
                        "event_subtype": CalendarEventTypeChoices.course,
                        "event_subtype_id": course.id,
                        "activity_date": course.start_date,
                        "ends_on": course.end_date,
                    }
                    user.related_calendar_activities.get_or_create(**activity_data)
                if course_modules:
                    self._create_event_for_course_modules(user=user, modules=course_modules)
                self._create_event_for_scheduled_session(users=[user], course=course)
        return True

    def _create_event_for_course_modules(self, user, modules):
        """Create a new calendar event for the specified course module."""

        for module in modules:
            activity_data = {
                "name": module.name,
                "description": module.description,
                "activity_type": ActivityTypeChoices.event,
                "event_subtype": CalendarEventTypeChoices.course,
                "event_subtype_id": module.course.id,
                "activity_date": module.start_date,
                "ends_on": module.end_date,
            }
            user.related_calendar_activities.get_or_create(**activity_data)
        return True

    def _create_event_for_scheduled_session(self, users, course=None, event_type=None, event_instance_id=None):
        """Create a new calendar event for the specified schedule session."""

        from apps.virtutor.models import ScheduledSession

        if not course and event_type == CalendarEventTypeChoices.session:
            sessions = ScheduledSession.objects.filter(id=event_instance_id)
        else:
            sessions = ScheduledSession.objects.filter(module__course=course, creator_role=RoleTypeChoices.admin)
        for session in sessions:
            for user in users:
                activity_data = {
                    "name": session.session_title,
                    "activity_type": ActivityTypeChoices.event,
                    "event_subtype": CalendarEventTypeChoices.session,
                    "event_subtype_id": session.module.course.id,
                    "activity_date": session.start_date,
                    "ends_on": session.end_date,
                }
                user.related_calendar_activities.get_or_create(**activity_data)
        return True

    def run(self, event_type: str, event_instance_id: int, user_ids, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User

        self.switch_db(db_name)
        self.logger.info("Executing CalendarActivityCreationTask")

        if isinstance(user_ids, int):
            user_ids = [user_ids]
        users = User.objects.filter(id__in=user_ids)
        match event_type:
            case CalendarEventTypeChoices.course:
                self._create_event_for_course(users, event_type=event_type, event_instance_id=event_instance_id)
            case CalendarEventTypeChoices.learning_path:
                self._create_event_for_lp(users, event_type=event_type, event_instance_id=event_instance_id)
            case CalendarEventTypeChoices.advanced_learning_path:
                self._create_event_for_alp(users, event_type=event_type, event_instance_id=event_instance_id)
            case CalendarEventTypeChoices.session:
                self._create_event_for_scheduled_session(
                    users=users, event_type=event_type, event_instance_id=event_instance_id
                )
        return True
