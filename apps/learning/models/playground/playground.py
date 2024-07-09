from django.db import models
from django.db.models import Sum

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
    ImageOnlyModel,
)
from apps.learning.config import PlaygroundGuidanceChoices, PlaygroundToolChoices, PlaygroundTypeChoices
from apps.learning.models import PlaygroundSkeletonModel


class PlaygroundImage(ImageOnlyModel):
    """
    Image model for Playground.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at
    """

    pass


class Playground(PlaygroundSkeletonModel):
    """
    Playground model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency, playground_type, guidance_type, tool
        Numeric     - rating, duration, certificate, learning_points,
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(PlaygroundSkeletonModel.Meta):
        default_related_name = "related_playgrounds"

    # FK
    image = models.ForeignKey(to=PlaygroundImage, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Choices
    playground_type = models.CharField(
        choices=PlaygroundTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    guidance_type = models.CharField(
        choices=PlaygroundGuidanceChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    tool = models.CharField(
        choices=PlaygroundToolChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )

    @property
    def file_url(self):
        """Returns the URL of the image."""

        return self.image.file_url if self.image else None

    def save(self, *args, **kwargs):
        """Overridden to update the course_code"""

        # TODO: handle the course_code generation in bulk creation of courses.
        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"PG_{self.pk + 1000}"
            self.save()
        return self


class PlaygroundGroupImage(ImageOnlyModel):
    """
    Image model for PlaygroundGroup.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at
    """

    pass


class PlaygroundGroup(PlaygroundSkeletonModel):
    """
    Playground Group Model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
        Numeric     - rating, duration, certificate, learning_points, no_of_playgrounds
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(PlaygroundSkeletonModel.Meta):
        default_related_name = "related_playground_groups"

    # FK
    image = models.ForeignKey(
        to=PlaygroundGroupImage, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Numeric
    no_of_playgrounds = models.PositiveIntegerField(default=0)

    @property
    def file_url(self):
        """Returns the URL of the image."""

        return self.image.file_url if self.image else None

    def dependent_numeric_fields_update(self):
        """Update the duration and no_of_playgrounds fields."""

        playground_relations = self.related_playground_relations.all()
        if not playground_relations:
            return None

        playgrounds = Playground.objects.filter(id__in=list(playground_relations.values_list("id", flat=True)))
        total_duration = playgrounds.aggregate(Sum("duration"))["duration__sum"]
        self.duration = total_duration or 0
        self.no_of_playgrounds = playground_relations.count()
        self.save()


class PlaygroundRelationModel(BaseModel):
    """
    Just a linker model between Playground & PlaygroundGroup.

    Model Fields -

        PK          - id,
        Fk          - playground, playground_group
        Numeric     - sequence
        Datetime    - created_at, modified_at
        Bool        - is_mandatory

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta:
        default_related_name = "related_playground_relations"

    playground = models.ForeignKey(to=Playground, on_delete=models.CASCADE)
    playground_group = models.ForeignKey(to=PlaygroundGroup, on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    is_mandatory = models.BooleanField(default=False)
