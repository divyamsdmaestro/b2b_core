import json

from django.core.files.storage import default_storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.managers import CourseSkeletonObjectManagerQuerySet
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    COMMON_URL_FIELD_MAX_LENGTH,
    BaseModel,
    CreationAndModificationModel,
    CUDArchivableModel,
    NameModel,
)
from apps.learning.config import (
    AssessmentProviderTypeChoices,
    AssessmentTypeChoices,
    BaseUploadStatusChoices,
    CourseResourceTypeChoices,
    ProficiencyChoices,
)
from apps.learning.tasks import UpdateCatalogueLearningDataTask
from apps.tenant_service.middlewares import get_current_db_name


class BaseCommonFieldModel(CUDArchivableModel, NameModel):
    """
    Learning Base Model with common fields.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
        Numeric     - rating, duration, learning_points,
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_rating_enabled,
                      is_feedback_mandatory

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    objects = CourseSkeletonObjectManagerQuerySet.as_manager()

    class Meta(CUDArchivableModel.Meta):
        abstract = True

    category = models.ForeignKey(
        to="learning.Category", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    language = models.ForeignKey(
        to="meta.Language", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # ManyToMany
    hashtag = models.ManyToManyField(to="meta.Hashtag", blank=True)

    # CharFields
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # TextFields
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    highlight = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    prerequisite = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Choices
    proficiency = models.CharField(
        choices=ProficiencyChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    # Numeric fields
    rating = models.FloatField(
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    learning_points = models.PositiveSmallIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    notify_days = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # DateTime Fields
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    retirement_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # BooleanFields
    is_archive = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    is_retired = models.BooleanField(default=False)
    is_rating_enabled = models.BooleanField(default=False)
    is_feedback_enabled = models.BooleanField(default=False)
    is_feedback_mandatory = models.BooleanField(default=False)
    feedback_template = models.ManyToManyField(to="meta.FeedbackTemplate", blank=True)
    is_notify_users = models.BooleanField(default=False)

    @property
    def highlight_as_list(self):
        """Convert from string to list of strings based on condition."""

        try:
            highlight = json.loads(f"{self.highlight}".strip()) if self.highlight else []
        except Exception:  # noqa
            highlight = [f"{self.highlight}".strip()] if self.highlight else []
        return highlight

    @highlight_as_list.setter
    def highlight_as_list(self, value):
        """highlight are stored on DB as a text json of the list object."""

        self.highlight = json.dumps(value)

    @property
    def hashtag_as_name(self):
        """Returns the hashtag names."""

        return self.hashtag.values_list("name", flat=True)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the catalogue learnings data."""

        instance = super().delete()
        catalogue_ids = list(self.related_learning_catalogues.all().values_list("id", flat=True))
        UpdateCatalogueLearningDataTask().run_task(catalogue_ids=catalogue_ids, db_name=get_current_db_name())
        return instance


class BaseLearningModel(BaseCommonFieldModel):
    """
    Learning Base Model with bool fields.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
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

    class Meta(BaseCommonFieldModel.Meta):
        abstract = True

    certificate = models.IntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    is_certificate_enabled = models.BooleanField(default=False)
    is_forum_enabled = models.BooleanField(default=False)
    is_assign_expert = models.BooleanField(default=False)
    is_dependencies_sequential = models.BooleanField(default=False)
    is_help_section_enabled = models.BooleanField(default=False)
    is_technical_support_enabled = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)


class BaseSkillLearningModel(BaseLearningModel):
    """
    Learning Base Model with skill.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - skill, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
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

    class Meta(BaseLearningModel.Meta):
        abstract = True

    skill = models.ManyToManyField(to="learning.CategorySkill", blank=True)


class BaseRoleSkillLearningModel(BaseLearningModel):
    """
    Learning Base Model with role & skill.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
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

    class Meta(BaseLearningModel.Meta):
        abstract = True

    skill = models.ManyToManyField(to="learning.CategorySkill", blank=True)
    role = models.ManyToManyField(to="learning.CategoryRole", blank=True)


class BaseResourceModel(CreationAndModificationModel, NameModel):
    """
    Base Resource model for IIHT-B2B.

    Model Fields -
        PK          - id,
        FK          - created_by, modified_by,
        Fields      - uuid, name, description
        Choices     - type, upload_status
        Numeric     - duration,
        Datetime    - created_at, modified_at
        URL         - file_url, custom_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(CreationAndModificationModel.Meta):
        abstract = True

    # CHAR Fields
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    type = models.CharField(choices=CourseResourceTypeChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    upload_status = models.CharField(choices=BaseUploadStatusChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    # URL Fields
    file_url = models.URLField(max_length=COMMON_URL_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    custom_url = models.CharField(max_length=COMMON_URL_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Numeric
    duration = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def delete(self, using=None, keep_parents=False):
        """Overridden to remove the file from django default_storage."""

        file_path = self.file_url
        instance = super().delete()
        if file_path and default_storage.exists(file_path):
            default_storage.delete(file_path)
        return instance

    def get_resource_type(self):
        """Returns the assessment type value"""

        return {"id": self.type, "name": CourseResourceTypeChoices.get_choice(self.type).label}


class BaseAssessmentModel(BaseModel):
    """
    Common model for IIHT-assessments.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    Fields      - name, type, provider_type, assessment_uuid
    Bool        - is_practice
    Datetime    - created_at, modified_at

    """

    class Meta(BaseModel.Meta):
        abstract = True

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    type = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=AssessmentTypeChoices.choices)
    provider_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=AssessmentProviderTypeChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    assessment_uuid = models.UUIDField()
    is_practice = models.BooleanField(default=False)
