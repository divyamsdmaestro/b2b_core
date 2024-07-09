from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Update assessment trackers for courses. Just a bugfix for data migration purpose only."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.tenant_service.middlewares import set_db_for_router

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        Enrollment = apps.get_model("my_learning", "Enrollment")
        CourseAssessment = apps.get_model("learning", "CourseAssessment")
        tenant_db_name = "some name"

        tracker = DatabaseRouter.objects.get(database_name=tenant_db_name)
        self.print_styled_message(f"\n** Adding Assessment Tracker for {tracker.database_name}. **")
        tracker.add_db_connection()
        set_db_for_router(tracker.database_name)

        enrollments = Enrollment.objects.filter(
            is_enrolled=True, user__isnull=False, learning_type="course", related_user_course_trackers__isnull=False
        )
        module_assessments = CourseAssessment.objects.filter(type="dependent_assessment", module__isnull=False)
        created_assessment_tracker_count = 0
        for enrollment in enrollments:
            course_trackers = enrollment.related_user_course_trackers.all()
            for course_tracker in course_trackers:
                course_assessments = course_tracker.course.related_course_assessments.all()
                for ca in course_assessments:
                    ca_tracker = course_tracker.related_course_assessment_trackers.filter(assessment=ca).first()
                    if not ca_tracker:
                        course_tracker.related_course_assessment_trackers.create(assessment=ca)
                        created_assessment_tracker_count += 1
                module_assessments = module_assessments.filter(module__course=course_tracker.course)
                for ma in module_assessments:
                    module_trackers = course_tracker.related_course_module_trackers.filter(module=ma.module).all()
                    for module_tracker in module_trackers:
                        ma_tracker = module_tracker.related_course_assessment_trackers.filter(assessment=ma).first()
                        if not ma_tracker:
                            module_tracker.related_course_assessment_trackers.create(assessment=ma)
                            created_assessment_tracker_count += 1
        self.print_styled_message(f"\n** Created Assessment Tracker Count {created_assessment_tracker_count}. **")
