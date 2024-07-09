from django.db import models

from apps.common.helpers import file_upload_path
from apps.common.model_fields import AppFileField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseUploadModel,
    ImageOnlyModel,
    NameModel,
)
from apps.learning.config import (
    AssignmentGuidanceChoices,
    AssignmentTypeChoices,
    EvaluationTypeChoices,
    PlaygroundToolChoices,
)
from apps.learning.models import BaseCommonFieldModel, BaseResourceModel
from apps.learning.validators import assignment_file_extension


class AssignmentTopic(NameModel):
    """
    Assignment topic model.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    Fields      - name
    Datetime    - created_at, modified_at

    """

    class Meta(NameModel.Meta):
        default_related_name = "related_assignment_topics"


class AssignmentSubTopic(NameModel):
    """
    Assignment subtopic model.

    ********************* Model Fields *********************

    PK          - id
    Unique      - uuid, ss_id
    Fields      - name
    Datetime    - created_at, modified_at

    """

    class Meta(NameModel.Meta):
        default_related_name = "related_assignment_subtopics"

    topic = models.ForeignKey(AssignmentTopic, on_delete=models.CASCADE)


class AssignmentImageModel(ImageOnlyModel):
    """
    Image model for assignment.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    class Meta(ImageOnlyModel.Meta):
        default_related_name = "related_assignment_images"


class AssignmentDocument(BaseUploadModel):
    """
    Assignment document model

    ********************* Model Fields *********************

    PK - id
    Unique - uuid
    Datetime - created_at, modified_at

    """

    file = AppFileField(max_size=5, upload_to=file_upload_path, validators=[assignment_file_extension])


class Assignment(BaseCommonFieldModel):
    """
    Assignment Model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image, author,
                      topic, sub_topic, file
        M2M         - skill, role, hashtag, feedback_template
        UUID        - uuid, mml_sku_id, assessment_uuid
        Fields      - name, description, highlight, prerequisite, vm_name, reference,
        Unique      - code
        Choices     - proficiency, type, tool, evaluation_type
        Numeric     - rating, duration, learning_points, version, allowed_attempts
        Date        - start_date, end_date, reminder_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_feedback_enabled, is_rating_enabled, send_reminder, enable_submission,
                      is_feedback_mandatory

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete, unarchived

    """

    class Meta(BaseCommonFieldModel.Meta):
        default_related_name = "related_assignments"

    # Foreignkey
    image = models.ForeignKey(
        AssignmentImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    author = models.ManyToManyField("access.User", blank=True)
    topic = models.ForeignKey(AssignmentTopic, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    subtopic = models.ForeignKey(
        AssignmentSubTopic, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    file = models.ForeignKey(AssignmentDocument, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # M2M
    skill = models.ManyToManyField(to="learning.CategorySkill", blank=True)
    role = models.ManyToManyField(to="learning.CategoryRole", blank=True)

    # UUID & Character & Text
    mml_sku_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    assessment_uuid = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    type = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=AssignmentTypeChoices.choices)
    tool = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=PlaygroundToolChoices.choices)
    evaluation_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=EvaluationTypeChoices.choices,
        default=EvaluationTypeChoices.evaluated,
    )
    guidance_type = models.CharField(
        choices=AssignmentGuidanceChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        default=AssignmentGuidanceChoices.guided,
    )
    guidance_text = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    reference = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Numeric
    allowed_attempts = models.IntegerField(default=1)
    version = models.FloatField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Date
    reminder_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Boolean
    send_reminder = models.BooleanField(default=False)
    enable_submission = models.BooleanField(default=False)

    def report_data(self):
        """Function to return assignment details for report."""

        return {
            "assignment_id": self.id,
            "assignment_uuid": self.uuid,
            "assignment_name": self.name,
            "assignment_code": self.code,
            "proficiency": self.proficiency,
            "learning_points": self.learning_points,
            "duration": self.duration,
            "skills": list(self.skill.all().values_list("name", flat=True)),
        }

    @classmethod
    def ccms_report_data(cls, data):
        """Function to return ccms assignment details for report."""

        return {
            "assignment_id": data["id"],
            "assignment_uuid": data["uuid"],
            "assignment_name": data["name"],
            "assignment_code": data["code"],
            "proficiency": data["proficiency"],
            "learning_points": data["learning_points"],
            "duration": data["duration"],
            "skills": data["skill"],
        }


class AssignmentResource(BaseResourceModel):
    """
    AssignmentResource model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - assignment
        Fields      - uuid, name, description
        Choices     - type, upload_status
        Numeric     - duration,
        Datetime    - created_at, modified_at
        URL         - file_url, custom_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseResourceModel.Meta):
        default_related_name = "related_assignment_resources"

    # FK
    assignment = models.ForeignKey(to=Assignment, on_delete=models.CASCADE)
