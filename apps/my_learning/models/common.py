from django.db import models

from apps.common.helpers import file_upload_path
from apps.common.model_fields import AppFileField
from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel


class BaseLearningFKModel(BaseModel):
    """Common model which has basic level FK fields. Just for DRY."""

    class Meta(BaseModel.Meta):
        abstract = True

    # ForeignKey fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    course = models.ForeignKey("learning.Course", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    learning_path = models.ForeignKey(
        "learning.LearningPath", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    advanced_learning_path = models.ForeignKey(
        "learning.AdvancedLearningPath", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    skill_traveller = models.ForeignKey(
        "learning.SkillTraveller", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    playground = models.ForeignKey(
        "learning.Playground", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    playground_group = models.ForeignKey(
        "learning.PlaygroundGroup", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    assignment = models.ForeignKey(
        "learning.Assignment", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    assignment_group = models.ForeignKey(
        "learning.AssignmentGroup", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    skill_ontology = models.ForeignKey(
        "learning.SkillOntology", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    ccms_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_ccms_obj = models.BooleanField(default=False)


class BaseYakshaSchedule(BaseModel):
    """
    Common model for yaksha assessment schedules.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id, scheduled_id
        URL         - scheduled_link
        Datetime    - created_at, modified_at
    """

    class Meta(BaseModel.Meta):
        abstract = True

    scheduled_id = models.IntegerField()
    scheduled_link = models.URLField()
    wecp_invite_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)


class BaseYakshaResult(BaseModel):
    """
    Common model for yaksha assessment results.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id
        Datetime    - created_at, modified_at
        Numeric     - attempt, duration, total_questions, answered, progress,
        DateTime    - start_time, end_time
        Bool        - is_pass
    """

    class Meta(BaseModel.Meta):
        abstract = True

    attempt = models.IntegerField()
    duration = models.IntegerField()
    total_questions = models.IntegerField()
    answered = models.IntegerField()
    progress = models.FloatField()
    start_time = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_time = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_pass = models.BooleanField()


class SubmissionFile(BaseModel):
    """
    File model for assignment submission.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id
        Datetime    - created_at, modified_at
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_submitted_files"

    file = AppFileField(max_size=5, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, upload_to=file_upload_path)

    @property
    def file_url(self):
        """Returns the image url if available."""

        return self.file.url if self.file else None


class BaseFileSubmission(BaseModel):
    """
    Common model for file submissions.

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid, ss_id
        FK          - evaluator
        M2M         - files
        Fields      - description, feedback
        Numeric     - attempt, progress,
        Datetime    - created_at, modified_at
        Bool        - is_pass, is_reviewed
    """

    class Meta(BaseModel.Meta):
        abstract = True

    evaluator = models.ForeignKey(
        to="access.User", on_delete=models.SET_DEFAULT, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    files = models.ManyToManyField(SubmissionFile)
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    feedback = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    attempt = models.PositiveIntegerField()
    pass_percentage = models.PositiveIntegerField(default=0)
    progress = models.FloatField(default=0)
    is_pass = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
