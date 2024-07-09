from djchoices import ChoiceItem, DjangoChoices


class NotifyActionChoices(DjangoChoices):
    """Holds the choices of Notification actions."""

    # Course
    self_course_enroll = ChoiceItem("self_course_enroll", "Self Course Enrollment")
    course_complete = ChoiceItem("course_complete", "Course Completion")
    course_assigned = ChoiceItem("course_assigned", "Course Assigned")
    # Learning Path
    self_lp_enroll = ChoiceItem("self_lp_enroll", "Self Learning Path Enrollment")
    lp_complete = ChoiceItem("lp_complete", "Learning Path Completion")
    lp_assigned = ChoiceItem("lp_assigned", "Learning Path Assigned")
    # Advanced Learning Path
    self_alp_enroll = ChoiceItem("self_alp_enroll", "Self Advanced Learning Path Enrollment")
    alp_complete = ChoiceItem("alp_complete", "Advanced Learning Path Completion")
    alp_assigned = ChoiceItem("alp_assigned", "Advanced Learning Path Assigned")
    # Skill Ontology
    skill_ontology_enroll = ChoiceItem("skill_ontology_enroll", "Skill Ontology Enrollment")
    skill_ontology_complete = ChoiceItem("skill_ontology_complete", "Skill Ontology Completion")
