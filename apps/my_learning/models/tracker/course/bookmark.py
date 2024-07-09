from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class UserCourseBookMark(BaseModel):
    """
    Bookmark model for user course.

    ********************* Model Fields *********************

    PK          - id
    FK          - created_by, sub_module_tracker
    Unique      - uuid
    Datetime    - created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none,
    """

    class Meta:
        default_related_name = "related_user_course_bookmarks"

    # FK Fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    sub_module_tracker = models.ForeignKey(
        "my_learning.CourseSubModuleTracker", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )  # TODO: need to remove the nullable config
