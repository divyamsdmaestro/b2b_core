from djchoices import ChoiceItem, DjangoChoices


class ActionChoices(DjangoChoices):
    """Choices for enrollment_action."""

    approved = ChoiceItem("approved", "Approved")
    rejected = ChoiceItem("rejected", "Rejected")
    pending = ChoiceItem("pending", "Pending")


class ApprovalTypeChoices(DjangoChoices):
    """Choices for approval type."""

    super_admin = ChoiceItem("super_admin", "Super Admin")
    tenant_admin = ChoiceItem("tenant_admin", "Tenant Admin")
    self_enrolled = ChoiceItem("self_enrolled", "Self Enrolled")


class LearningStatusChoices(DjangoChoices):
    """Choices for LearningStatus."""

    not_started = ChoiceItem("not_started", "Not Started")
    started = ChoiceItem("started", "Started")
    in_progress = ChoiceItem("in_progress", "In Progress")
    completed = ChoiceItem("completed", "Completed")


class BaseLearningTypeChoices(DjangoChoices):
    """Choices for learning model FKs."""

    course = ChoiceItem("course", "Course")
    learning_path = ChoiceItem("learning_path", "Learning Path")
    advanced_learning_path = ChoiceItem("advanced_learning_path", "Advanced Learning Path")
    skill_traveller = ChoiceItem("skill_traveller", "Skill Traveller")


class AllBaseLearningTypeChoices(BaseLearningTypeChoices):
    """Choices for learning model FKs."""

    playground = ChoiceItem("playground", "Playground")
    playground_group = ChoiceItem("playground_group", "Playground Group")
    assignment = ChoiceItem("assignment", "Assignment")
    assignment_group = ChoiceItem("assignment_group", "Assignment Group")


class AssignmentLearningTypeChoices(BaseLearningTypeChoices):
    """Choices for assignment start types."""

    assignment = ChoiceItem("assignment", "Assignment")


class MilestoneCategoryTypeChoices(AllBaseLearningTypeChoices):
    """Choices for assessment"""

    assessment = ChoiceItem("assessment", "Assessment")
    forum = ChoiceItem("forum", "Forum")


class EnrollmentTypeChoices(AllBaseLearningTypeChoices):
    """Choices for enrollment_type."""

    skill_ontology = ChoiceItem("skill_ontology", "Skill Ontology")


class RatingTypeChoices(AllBaseLearningTypeChoices):
    """Choices for enrollment_type."""

    skill_ontology = ChoiceItem("skill_ontology", "Skill Ontology")


class FavouriteTypeChoices(AllBaseLearningTypeChoices):
    """Holds the  favourite type choices."""

    category = ChoiceItem("category", "Category")
    skill = ChoiceItem("skill", "Skill")
    role = ChoiceItem("role", "Role")
    skill_ontology = ChoiceItem("skill_ontology", "Skill Ontology")


class AnnouncementTypeChoices(DjangoChoices):
    """Choices for announcement types."""

    user_level = ChoiceItem("user_level", "User Level")
    user_group_level = ChoiceItem("user_group_level", "User Group Level")
    tenant_level = ChoiceItem("tenant_level", "Tenant Level")
