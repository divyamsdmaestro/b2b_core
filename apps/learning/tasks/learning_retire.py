from datetime import datetime

from apps.tenant_service.middlewares import set_db_for_router
from config.celery_app import app as celery_app


@celery_app.task
def handle_learning_retire():
    """Cron job to retire the learnings."""

    print("Learning Retirement Task - working")
    from apps.learning.config import BaseUploadStatusChoices
    from apps.learning.models import (
        AdvancedLearningPath,
        Assignment,
        AssignmentGroup,
        Course,
        LearningPath,
        SkillTraveller,
    )
    from apps.tenant_service.models import DatabaseRouter

    current_date = datetime.today().date()
    filter_params = {
        "is_retired": False,
        "retirement_date__lt": current_date,
    }
    set_db_for_router()
    for router in DatabaseRouter.objects.filter(setup_status=BaseUploadStatusChoices.completed):
        print(f"\n** Getting Retirement Objects for {router.database_name}. **")
        router.add_db_connection()
        set_db_for_router(router.database_name)
        Course.objects.filter(**filter_params).update(is_retired=True, is_active=False)
        LearningPath.objects.filter(**filter_params).update(is_retired=True, is_active=False)
        AdvancedLearningPath.objects.filter(**filter_params).update(is_retired=True, is_active=False)
        SkillTraveller.objects.filter(**filter_params).update(is_retired=True, is_active=False)
        Assignment.objects.filter(**filter_params).update(is_retired=True, is_active=False)
        AssignmentGroup.objects.filter(**filter_params).update(is_retired=True, is_active=False)
        set_db_for_router()
    return True
