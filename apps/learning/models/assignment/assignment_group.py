from django.apps import apps
from django.db import models
from django.db.models import F, Sum

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, ImageOnlyModel
from apps.common.models.base import BaseModel
from apps.learning.models import BaseCommonFieldModel


class AssignmentGroupImageModel(ImageOnlyModel):
    """
    Image model for assignment group.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    class Meta(ImageOnlyModel.Meta):
        default_related_name = "related_assignment_group_images"


class AssignmentGroup(BaseCommonFieldModel):
    """
    AssignmentGroup Model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image
        M2M         - hashtag, feedback_template, skill, role
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency
        Numeric     - rating, duration, learning_points, no_of_assignments
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_rating_enabled,
                      is_feedback_mandatory

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(BaseCommonFieldModel.Meta):
        default_related_name = "related_assignment_groups"

    # Foreignkey
    image = models.ForeignKey(
        AssignmentGroupImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # M2M
    skill = models.ManyToManyField(to="learning.CategorySkill", blank=True)
    role = models.ManyToManyField(to="learning.CategoryRole", blank=True)
    # Numeric
    no_of_assignments = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        """Overridden to update the assignment group code"""

        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"PG_{self.pk + 1000}"
            self.save()
        return self

    @property
    def assignments(self):
        """Returns all the associated assignments."""

        from apps.learning.models.assignment.assignment import Assignment

        assignment_ids = self.related_assignment_relations.all().values_list("assignment", flat=True)
        return Assignment.objects.filter(pk__in=assignment_ids).alive()

    def duration_and_count_update(self):
        """Update the duration based on the assigned courses."""

        AssignmentKlass = apps.get_model("learning.Assignment")
        assignment_ids = self.related_assignment_relations.all().values_list("assignment_id")
        related_assignments = AssignmentKlass.objects.filter(id__in=assignment_ids).alive()
        tot_duration = related_assignments.aggregate(Sum("duration"))["duration__sum"]
        self.duration = tot_duration or 0
        self.no_of_assignments = related_assignments.count()
        self.save()

    def recalculate_dependencies_sequence(self, from_sequence):
        """Called when assignment relation has been deleted."""

        queryset = self.related_assignment_relations.order_by("sequence")
        queryset = queryset.filter(sequence__gt=from_sequence)
        queryset.update(sequence=F("sequence") - 1)

    def report_data(self):
        """Function to return ag details for report."""

        return {
            "ag_id": self.id,
            "ag_uuid": self.uuid,
            "ag_name": self.name,
            "ag_code": self.code,
            "proficiency": self.proficiency,
            "learning_points": self.learning_points,
            "duration": self.duration,
            "skills": list(self.skill.all().values_list("name", flat=True)),
        }


class AssignmentRelation(BaseModel):
    """
    Course Model related to Assignment Relation.

    Model Fields -

        PK          - id,
        Fk          - assignment_group, assignment
        Numeric     - sequence
        Datetime    - created_at, modified_at
        Bool        - is_mandatory

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta:
        default_related_name = "related_assignment_relations"

    assignment_group = models.ForeignKey(to=AssignmentGroup, on_delete=models.CASCADE)
    assignment = models.ForeignKey(to="learning.Assignment", on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    is_mandatory = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the assignment sequence when the assignment relation is deleted."""

        instance = super().delete()
        self.assignment_group.duration_and_count_update()
        self.assignment_group.recalculate_dependencies_sequence(from_sequence=self.sequence)
        return instance
