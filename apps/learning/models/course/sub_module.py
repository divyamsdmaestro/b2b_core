import uuid

from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, CUDSoftDeleteModel
from apps.learning.config import EvaluationTypeChoices, SubModuleTypeChoices
from apps.learning.models import BaseResourceModel


class CourseSubModule(CUDSoftDeleteModel, BaseResourceModel):
    """
    CourseSubModule model for IIHT-B2B.

    Model Fields -
        PK          - id,
        FK          - created_by, modified_by, deleted_by, module
        M2M         - author
        Fields      - uuid, name, description, type, upload_status, file_url, custom_url
        Numeric     - sequence, duration
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_deleted, is_draft

    App QuerySet Manager Methods -
        get_or_none, alive, dead, delete, hard_delete
    """

    class Meta(CUDSoftDeleteModel.Meta):
        default_related_name = "related_course_sub_modules"

    # FK Fields
    module = models.ForeignKey("learning.CourseModule", on_delete=models.CASCADE)
    author = models.ManyToManyField("access.User", blank=True)

    # Fields
    type = models.CharField(choices=SubModuleTypeChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    sequence = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_draft = models.BooleanField(default=True)
    evaluation_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=EvaluationTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the duration of modules."""

        instance = super().delete()
        self.module.module_duration_update()
        self.module.course.course_duration_count_update()
        return instance

    def get_resource_type(self):
        """Returns the assessment type value"""

        return {"id": self.type, "name": SubModuleTypeChoices.get_choice(self.type).label}

    def duration_update(self):
        """Called when the file upload has finished to auto calculate duration of video."""

        self.module.module_duration_update()
        self.module.course.course_duration_count_update()

    def clone(self, module_id):
        """Clone the submodule."""

        cloned_sub_module: CourseSubModule = CourseSubModule.objects.get(pk=self.id)
        cloned_sub_module.id = None
        cloned_sub_module.module_id = module_id
        cloned_sub_module.uuid = uuid.uuid4()
        cloned_sub_module.save()
        return {"cloned_sub_module_id": cloned_sub_module.id}
