from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class UserCourseNotes(BaseModel):
    """
    Notes model for user course.

    ********************* Model Fields *********************

    PK          - id
    FK          - created_by, modified_by, deleted_by, sub_module
    Unique      - uuid
    Datetime    - created_at, modified_at, deleted_at
    Text        - notes
    Numeric     - time_stamp
    Bool        - is_deleted

    App QuerySet Manager Methods -
        get_or_none, alive, delete, hard_delete
    """

    class Meta:
        default_related_name = "related_user_course_notes"

    # FK Fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    notes = models.TextField()
    sub_module = models.ForeignKey("learning.CourseSubModule", on_delete=models.CASCADE)
    time_stamp = models.FloatField()
