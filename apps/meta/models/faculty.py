from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    CreationAndModificationModel,
    ImageOnlyModel,
    NameModel,
)
from apps.meta.config import FacultyTypeChoices


class FacultyImageModel(ImageOnlyModel):
    """
    Image model for Faculty.

    Model Fields -
        PK          - id,
        Fields      - uuid, image
        Datetime    - created_at, modified_at
        FK          - created_by

    """

    pass


class Faculty(CreationAndModificationModel, NameModel):
    """
    Faculty Meta model for IIHT-B2B.

    ********************* Model Fields *********************

    PK          - id
    FK          - created_by, modified_by, faculty_image
    Unique      - uuid
    Fields      - name, description, type
    Numeric     - rating, no_of_students, no_of_courses
    Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    # FKs
    faculty_image = models.ForeignKey(
        to=FacultyImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # Fields
    type = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=FacultyTypeChoices.choices)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    rating = models.FloatField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    no_of_students = models.PositiveIntegerField(default=0)
    no_of_courses = models.PositiveIntegerField(default=0)

    def get_faculty_type(self):
        """Returns the type with id & name."""

        return {"id": self.type, "name": FacultyTypeChoices.get_choice(self.type).label}
