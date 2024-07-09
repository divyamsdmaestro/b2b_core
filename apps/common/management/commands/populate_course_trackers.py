from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Update category and skills to catalogue. Just a bugfix for data migration purpose only."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.my_learning.config import EnrollmentTypeChoices
        from apps.tenant_service.middlewares import set_db_for_router

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        Enrollment = apps.get_model("my_learning", "Enrollment")
        tenant_db_name = "b2b-uat"

        tracker = DatabaseRouter.objects.get(database_name=tenant_db_name)
        self.print_styled_message(f"\n** Populating Course Trackers And Dependencies for {tracker.database_name}. **")
        tracker.add_db_connection()
        set_db_for_router(tracker.database_name)

        enrollments = Enrollment.objects.filter(
            learning_type=EnrollmentTypeChoices.course,
            is_enrolled=True,
        )
        for enrollment in enrollments:
            user = enrollment.user
            course = enrollment.course
            if user and course:
                self.add_course_trackers(user, course, enrollment)
            else:
                continue

    def add_course_trackers(self, user, course, enrollment):
        """Adding Course Trackers."""

        from apps.my_learning.config import LearningStatusChoices

        self.print_styled_message(f"\n** Adding course({course.name}) tracker for {user.name}. **")

        course_tracker, created = user.related_user_course_trackers.update_or_create(
            course=course, defaults={"enrollment": enrollment}
        )
        self.add_module_submodule_trackers(course_tracker, course)
        course_tracker.enrollment.learning_status = LearningStatusChoices.started
        course_tracker.enrollment.save()

        self.print_styled_message(f"\n** Course({course.name}) tracker successfully added for {user.name}. **")

    def add_module_submodule_trackers(self, course_tracker, course):
        """Adding Module Trackers and SubModule Trackers.."""

        modules = course.related_course_modules.alive()
        for module in modules:
            self.print_styled_message(f"\n** Adding module({module.name}) tracker for {course.name}. **")
            module_parent_tracker, _ = course_tracker.related_course_module_trackers.update_or_create(module=module)
            sub_modules = module.related_course_sub_modules.alive()
            for sub_module in sub_modules:
                self.print_styled_message(f"\n** Adding submodule({sub_module.name}) tracker for {module.name}. **")
                module_parent_tracker.related_course_sub_module_trackers.update_or_create(sub_module=sub_module)
                self.print_styled_message(
                    f"\n** SubModule({sub_module.name}) tracker successfully added for {module.name}. **"
                )
            self.print_styled_message(f"\n** Module({module.name}) tracker successfully added for {course.name}. **")
        return True
