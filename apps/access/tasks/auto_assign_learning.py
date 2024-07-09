from django.utils import timezone

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import AllBaseLearningTypeChoices, ApprovalTypeChoices


class AutoAssignLearningTask(BaseAppTask):
    """Task to Auto  the Users"""

    def auto_assign_course_and_catalog(self, user):
        """Function to add catalog and assign mandatory courses to user."""

        from apps.learning.models import CatalogueRelation, Course
        from apps.my_learning.models import Enrollment

        catalogs_relations = CatalogueRelation.objects.filter(catalogue__id__in=[8868, 8870])
        for catalogs_relation in catalogs_relations:
            catalogs_relation.user.add(user)
        user_groups = user.related_user_groups.all()
        courses = (
            Course.objects.unarchived()
            .filter(id__in=[14079, 15635, 15636, 15663, 15664])
            .exclude(related_enrollments__user_group__in=user_groups)
        )
        enrollment_objs = []
        for course in courses:
            enrollment_objs.append(
                Enrollment(
                    **{
                        "user_id": user.id,
                        "course_id": course.id,
                        "learning_type": AllBaseLearningTypeChoices.course,
                        "created_by_id": user.id,
                        "action": "approved",
                        "action_date": timezone.now().date(),
                        "actionee_id": user.id,
                        "approval_type": ApprovalTypeChoices.tenant_admin,
                        "reason": "Auto Assign Courses - Prolifics",
                        "is_enrolled": True,
                        "end_date": None,
                    }
                )
            )
        Enrollment.objects.bulk_create(enrollment_objs)
        return True

    def run(self, user_id, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User

        self.switch_db(db_name)
        self.logger.info("Executing AutoAssignLearningTask.")

        user = User.objects.get(id=user_id)
        self.auto_assign_course_and_catalog(user)

        return True
