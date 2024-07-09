from django.db import models

from apps.common.models.base import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, NameModel


class SkillOntology(NameModel):
    """
    Skill Ontology model for IIHT-B2B.

    Model Fields -
        PK          - id,
        FK          - user, current_skill_detail, desired_skill_detail,
        M2M         - course, learning_path, advanced_learning_path, skill_traveller,
                      assignment, assignment_group
        Fields      - uuid, name
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(NameModel.Meta):
        default_related_name = "related_skill_ontologies"

    # FK
    user = models.ForeignKey("access.User", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    current_skill_detail = models.ForeignKey(
        "access.UserSkillDetail",
        on_delete=models.SET_NULL,
        related_name="related_current_skill_detail",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    desired_skill_detail = models.ForeignKey(
        "access.UserSkillDetail",
        on_delete=models.SET_NULL,
        related_name="related_desired_skill_detail",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # MtoM
    course = models.ManyToManyField("learning.Course", blank=True)
    learning_path = models.ManyToManyField("learning.LearningPath", blank=True)
    advanced_learning_path = models.ManyToManyField("learning.AdvancedLearningPath", blank=True)
    skill_traveller = models.ManyToManyField("learning.SkillTraveller", blank=True)
    assignment = models.ManyToManyField("learning.Assignment", blank=True)
    assignment_group = models.ManyToManyField("learning.AssignmentGroup", blank=True)

    def report_data(self):
        """Function to return so details for report."""

        cur_skill = self.current_skill_detail
        desired_skill = self.desired_skill_detail
        return {
            "so_id": self.id,
            "so_uuid": self.uuid,
            "so_name": self.name,
            "skills": [cur_skill.skill.name, desired_skill.skill.name],
            "proficiency": f"{cur_skill.proficiency}, {desired_skill.proficiency}",
        }
