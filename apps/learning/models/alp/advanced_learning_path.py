from django.db import models
from django.db.models import F, Sum

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel, ImageOnlyModel
from apps.learning.models import BaseResourceModel, LearningPath, LearningPathCommonModel


class AdvancedLearningPathImageModel(ImageOnlyModel):
    """
    Image model for advanced learning paths.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class AdvancedLearningPath(LearningPathCommonModel):
    """
    Advanced Learning path model for IIHT-B2B.

    Model Fields -

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency, learning_type
        Numeric     - rating, duration, certificate, learning_points, no_of_lp
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(LearningPathCommonModel.Meta):
        default_related_name = "related_advanced_learning_paths"

    # FK
    image = models.ForeignKey(
        to=AdvancedLearningPathImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # ManyToManyField
    forums = models.ManyToManyField(to="forum.Forum", blank=True)

    # Numeric
    no_of_lp = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        """Overridden to update the advanced_learning_path_code"""

        # TODO: handle the course_code generation in bulk creation of courses.
        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"ALP_{self.pk + 1000}"
            self.save()

        return self

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the role, category & skills learning_path counts when the alp is deleted."""

        instance = super().delete()
        self.role.all().role_advanced_learning_path_count_update()
        self.skill.all().skill_advanced_learning_path_count_update()
        self.category.category_advanced_learning_path_count_update()

        return instance

    @property
    def learning_paths(self):
        """Returns all the associated learning paths."""

        assigned_lp_pk = self.related_alp_learning_paths.all().values_list("learning_path")
        return LearningPath.objects.filter(pk__in=assigned_lp_pk)

    def duration_lp_count_update(self):
        """Update the duration based on the assigned learning_paths."""

        assigned_lp_pk = self.related_alp_learning_paths.all().values_list("learning_path")
        assigned_learning_paths = LearningPath.objects.filter(pk__in=assigned_lp_pk).alive()
        tot_duration = assigned_learning_paths.aggregate(Sum("duration"))["duration__sum"]
        self.duration = tot_duration or 0
        self.no_of_lp = assigned_learning_paths.count()
        self.save()

    def recalculate_alp_dependencies_sequence(self, assessment=False, assignment=False, from_sequence=None):
        """Called when dependencies has been deleted & to update all the dependencies to the new sequence."""

        instances = self.related_alp_learning_paths.order_by("sequence")
        if assessment:
            instances = self.related_alp_assessments.order_by("sequence")
        elif assignment:
            instances = self.related_alp_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, st_course in enumerate(instances, start=1):
                st_course.sequence = index
                st_course.save(update_fields=["sequence"])

    def report_data(self):
        """Function to return alp details for report."""

        return {
            "alp_id": self.id,
            "alp_uuid": self.uuid,
            "alp_name": self.name,
            "alp_code": self.code,
            "proficiency": self.proficiency,
            "learning_points": self.learning_points,
            "duration": self.duration,
            "skills": list(self.skill.all().values_list("name", flat=True)),
        }

    @classmethod
    def ccms_report_data(cls, data):
        """Function to return ccms alp details for report."""

        return {
            "alp_id": data["id"],
            "alp_uuid": data["uuid"],
            "alp_name": data["name"],
            "alp_code": data["code"],
            "proficiency": data["proficiency"],
            "learning_points": data["learning_points"],
            "duration": data["duration"],
            "skills": data["skill"],
        }


class ALPLearningPath(BaseModel):
    """
    LearningPathModel related to advanced learning path.

    Model Fields -

        PK          - id,
        Fk          - advanced_learning_path, course
        Numeric     - sequence
        Datetime    - created_at, modified_at
        Bool        - is_mandatory,

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta:
        default_related_name = "related_alp_learning_paths"

    advanced_learning_path = models.ForeignKey(to=AdvancedLearningPath, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(to="learning.LearningPath", on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    is_mandatory = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the learning_path course count when the course is deleted."""

        instance = super().delete()
        self.advanced_learning_path.duration_lp_count_update()
        self.advanced_learning_path.recalculate_alp_dependencies_sequence(from_sequence=self.sequence)
        return instance

    def recalculate_alp_lp_dependencies_sequence(self, assignment=False, from_sequence=None):
        """
        Called when alp's lp dependencies has been deleted & to update all the dependencies to new sequence.
        """

        instances = self.related_alp_assessments.order_by("sequence")
        if assignment:
            instances = self.related_alp_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, lp_course in enumerate(instances, start=1):
                lp_course.sequence = index
                lp_course.save(update_fields=["sequence"])


class AdvancedLearningPathResource(BaseResourceModel):
    """
    AdvancedLearningPathResource model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - advanced_learning_path
        Fields      - uuid, name, description
        Choices     - type, upload_status
        Numeric     - duration,
        Datetime    - created_at, modified_at
        URL         - file_url, custom_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseResourceModel.Meta):
        default_related_name = "related_advanced_learning_path_resources"

    # FK
    advanced_learning_path = models.ForeignKey(to=AdvancedLearningPath, on_delete=models.CASCADE)
