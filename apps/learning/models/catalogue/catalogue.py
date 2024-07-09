import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel
from apps.learning.models.talent_management.common import PerformanceMetrix


class Catalogue(PerformanceMetrix):
    """
    Catalogue model for IIHT-B2B.

    ********************* Model Fields *********************
        PK              - id,
        Fk              - created_by, modified_by, deleted_by,
        M2M             - course, learning_path, advanced_learning_path
                          skill_traveller, playground, playground_group, category,
                          role, skill, assignment
        Fields          - uuid, name, description
        Unique          - code
        ArrayFields     - ccms_course, ccms_lp, ccms_alp, ccms_st, ccms_tp, ccms_tpg, ccms_assignment,
        Numeric         - no_of_course, no_of_lp, no_of_alp,
                          no_of_st, no_of_tp, no_of_tpg, no_of_assignment, no_of_assignment_group
        Datetime        - created_at, modified_at, deleted_at
        Bool            - is_active, is_deleted, is_draft, is_assessment_enabled, is_labs_enabled, is_locked
    """

    class Meta(PerformanceMetrix.Meta):
        default_related_name = "related_learning_catalogues"

    # ManyToMany fields
    course = models.ManyToManyField("learning.Course", blank=True)
    learning_path = models.ManyToManyField("learning.LearningPath", blank=True)
    advanced_learning_path = models.ManyToManyField("learning.AdvancedLearningPath", blank=True)
    skill_traveller = models.ManyToManyField("learning.SkillTraveller", blank=True)
    playground = models.ManyToManyField("learning.Playground", blank=True)
    playground_group = models.ManyToManyField("learning.PlaygroundGroup", blank=True)
    assignment = models.ManyToManyField("learning.Assignment", blank=True)
    assignment_group = models.ManyToManyField("learning.AssignmentGroup", blank=True)
    category = models.ManyToManyField(to="learning.Category", blank=True)
    skill = models.ManyToManyField(to="learning.CategorySkill", blank=True)
    role = models.ManyToManyField(to="learning.CategoryRole", blank=True)

    # ArrayField
    ccms_course = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_lp = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_alp = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_st = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_tp = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_tpg = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_assignment = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    ccms_assignment_group = ArrayField(base_field=models.UUIDField(), **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # CharFields
    code = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    is_assessment_enabled = models.BooleanField(default=False)
    is_labs_enabled = models.BooleanField(default=False)
    is_self_enroll_enabled = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    def update_catalogue_learning_counts(self):
        """Update the counts of various learning items assigned to the catalogue."""

        self.no_of_course = self.course.alive().count() + len(self.ccms_course or [])
        self.no_of_lp = self.learning_path.alive().count() + len(self.ccms_lp or [])
        self.no_of_alp = self.advanced_learning_path.alive().count() + len(self.ccms_alp or [])
        self.no_of_st = self.skill_traveller.alive().count() + len(self.ccms_st or [])
        self.no_of_tp = self.playground.alive().count() + len(self.ccms_tp or [])
        self.no_of_tpg = self.playground_group.alive().count() + len(self.ccms_tpg or [])
        self.no_of_assignment = self.assignment.alive().count() + len(self.ccms_assignment or [])
        self.no_of_assignment_group = self.assignment_group.alive().count() + len(self.ccms_assignment_group or [])
        self.save()

    def save(self, *args, **kwargs):
        """Overridden to update the catalogue code"""

        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"CATALOGUE_{self.pk + 1000}"
            self.save()
        return self

    def clone(self):
        """Clone the catalogue instance."""

        cloned_catalogue = Catalogue.objects.get(pk=self.id)
        cloned_catalogue.id = None
        cloned_catalogue.code = None
        cloned_catalogue.name = f"{self.name}_{self.pk + 1000}"
        cloned_catalogue.uuid = uuid.uuid4()
        cloned_catalogue.save()
        cloned_catalogue.course.set(self.course.all())
        cloned_catalogue.learning_path.set(self.learning_path.all())
        cloned_catalogue.advanced_learning_path.set(self.advanced_learning_path.all())
        cloned_catalogue.skill_traveller.set(self.skill_traveller.all())
        cloned_catalogue.assignment.set(self.assignment.all())
        cloned_catalogue.assignment_group.set(self.assignment_group.all())
        cloned_catalogue.category.set(self.category.all())
        cloned_catalogue.role.set(self.role.all())
        cloned_catalogue.skill.set(self.skill.all())
        return {"cloned_catalogue_id": cloned_catalogue.id}


class CatalogueRelation(BaseModel):
    """
    Catalogue relations model have user relations.

    ********************* Model Fields *********************
        PK          - id,
        One2One     - catalogue,
        M2M         - user_group, user,
        Fields      - uuid, ccms_id,
        Bool        - is_ccms_obj,
        Datetime    - created_at, modified_at,
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_catalogue_relations"

    catalogue = models.OneToOneField(Catalogue, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    user_group = models.ManyToManyField("access_control.UserGroup", blank=True)
    user = models.ManyToManyField("access.User", blank=True)
    ccms_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, unique=True)
    is_ccms_obj = models.BooleanField(default=False)
