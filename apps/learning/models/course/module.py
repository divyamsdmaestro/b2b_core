import uuid

from django.db import models
from django.db.models import F, Sum

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, CUDSoftDeleteModel, NameModel


class CourseModule(CUDSoftDeleteModel, NameModel):
    """
    CourseModule model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, deleted_by, course,
        Fields      - uuid, name, description,
        Numeric     - sequence, duration,
        Date        - start_date, end_date,
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_deleted, is_draft, is_mandatory,

    App QuerySet Manager Methods -
        get_or_none, alive, dead, delete, hard_delete
    """

    class Meta(CUDSoftDeleteModel.Meta):
        default_related_name = "related_course_modules"

    course = models.ForeignKey("learning.Course", on_delete=models.CASCADE)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    duration = models.PositiveIntegerField(default=0)
    sequence = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_mandatory = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)

    def delete(self, using=None, keep_parents=False):
        """Overridden to delete the dependent sub_modules."""

        instance = super().delete()
        self.related_course_sub_modules.all().delete()
        self.course.course_duration_count_update()
        self.course.recalculate_course_dependencies_sequence()
        return instance

    def module_duration_update(self):
        """Update the duration based on the sub_modules."""

        tot_sub_module = self.related_course_sub_modules.alive().aggregate(Sum("duration"))
        self.duration = tot_sub_module["duration__sum"] if tot_sub_module["duration__sum"] else 0
        self.save()
        return True

    def recalculate_module_dependencies_sequence(self, assessment=False, assignment=False, from_sequence=None):
        """Called when module dependencies has been deleted & to update all the dependencies to new sequence."""

        instances = self.related_course_sub_modules.order_by("sequence")
        if assessment:
            instances = self.related_course_assessments.order_by("sequence")
        elif assignment:
            instances = self.related_course_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, instance in enumerate(instances, start=1):
                instance.sequence = index
                instance.save(update_fields=["sequence"])
        return True

    def clone(self, course_id):
        """Clone the module and related models."""

        cloned_module: CourseModule = CourseModule.objects.get(pk=self.id)
        cloned_module.id = None
        cloned_module.course_id = course_id
        cloned_module.uuid = uuid.uuid4()
        cloned_module.save()
        for sub_module in self.related_course_sub_modules.all():
            sub_module.clone(module_id=cloned_module.id)
        return {"cloned_module_id": cloned_module.id}
