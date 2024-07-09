from djchoices import ChoiceItem, DjangoChoices


class MilestoneChoices(DjangoChoices):
    """Holds the choices of forum types."""

    first_course_enroll = ChoiceItem("first_course_enroll", "First Course Enrolment")
    first_course_complete = ChoiceItem("first_course_complete", "First Course Completion")
    first_learning_path_enroll = ChoiceItem("first_learning_path_enroll", "First Learning Path Enrolment")
    first_learning_path_complete = ChoiceItem("first_learning_path_complete", "First Learning Path Completion")
    course_self_enroll = ChoiceItem("course_self_enroll", "Course Self Enrolled")
    course_assigned = ChoiceItem("course_assigned", "Course Assigned")
    learning_path_self_enroll = ChoiceItem("learning_path_self_enroll", "Learning Path Self Enrolled")
    learning_path_assigned = ChoiceItem("learning_path_assigned", "Learning Path Assigned")
    upload_profile_picture = ChoiceItem("upload_profile_picture", "Upload Profile Picture")
    first_login = ChoiceItem("first_login", "First Login")
    module_completion_in_first_enrolled_course = ChoiceItem(
        "module_completion_in_first_enrolled_course", "Module Completion In First Enrolled Course"
    )
    forum_post_creation = ChoiceItem("forum_post_creation", "Forum Post Creation")
    forum_post_comments = ChoiceItem("forum_post_comments", "Forum Post Comments")
    replying_comments = ChoiceItem("replying_comments", "Replying Comments")
    yaksha_completion = ChoiceItem("yaksha_completion", "Yaksha Completion")
    yaksha_champion = ChoiceItem("yaksha_champion", "Yaksha Champion")
    assignment_submission = ChoiceItem("assignment_submission", "Assignment Submission")
    assignment_completion = ChoiceItem("assignment_completion", "Assignment Completion")
    quick_finisher_self_enrolled_course = ChoiceItem(
        "quick_finisher_self_enrolled_course", "Quick Finisher Self Enrolled Course"
    )
    quick_finisher_assigned_course = ChoiceItem("quick_finisher_assigned_course", "Quick Finisher Assigned Course")
    quick_finisher_self_enrolled_lp = ChoiceItem(
        "quick_finisher_self_enrolled_learning_path", "Quick Finisher Self Enrolled Learning Path"
    )
    quick_finisher_assigned_lp = ChoiceItem(
        "quick_finisher_assigned_learning_path", "Quick Finisher Assigned Learning Path"
    )
    learning_path_starter = ChoiceItem("learning_path_starter", "Learning Path Starter")
    skill_achiever = ChoiceItem("skill_achiever", "Skill Achiever")
    proficiency_achiever = ChoiceItem("proficiency_achiever", "Proficiency Achiever")
    leaderboard_level_promoted = ChoiceItem("leaderboard_level_promoted", "Leaderboard Level Promoted")
    course_certificate_earned = ChoiceItem("course_certificate_earned", "Course Certificate Earned")
    expertise_accomplishment = ChoiceItem("expertise_accomplishment", "Expertise Accomplishment")
    following_expert = ChoiceItem("following_expert", "Following Expert")
    profile_completion = ChoiceItem("profile_completion", "Profile Completion")
    replying_comments_as_expert = ChoiceItem("replying_comments_as_expert", "Replying Comments As Expert")
    replying_comments_as_expert_ontime = ChoiceItem(
        "replying_comments_as_expert_ontime", "Replying Comments As Expert Ontime"
    )
    forum_creation = ChoiceItem("forum_creation", "Forum Creation")
    learning_path_certificate_earned = ChoiceItem(
        "learning_path_certificate_earned", "Learning Path Certificate Earned"
    )
    first_certification_path_enrollment = ChoiceItem(
        "first_certification_path_enrollment", "First Certification Path Enrollment"
    )
    first_certification_path_completion = ChoiceItem(
        "first_certification_path_completion", "First Certification Path Completion"
    )
    certification_path_self_enrolled = ChoiceItem(
        "certification_path_self_enrolled", "Certification Path Self Enrolled"
    )
    certification_path_assigned = ChoiceItem("certification_path_assigned", "Certification Path Assigned")
    quick_finisher_self_enrolled_certification_path = ChoiceItem(
        "quick_finisher_self_enrolled_certification_path", "Quick Finisher Self Enrolled Certification Path"
    )
    quick_finisher_assigned_certification_path = ChoiceItem(
        "quick_finisher_assigned_certification_path", "Quick Finisher Assigned Certification Path"
    )
    certification_path_starter = ChoiceItem("certification_path_starter", "Certification Path Starter")
    certification_path_certificate_earned = ChoiceItem(
        "certification_path_certificate_earned", "Certification Path Certificate Earned"
    )
    yaksha_module_completion = ChoiceItem("yaksha_module_completion", "Yaksha Module Completion")
    mml_progress = ChoiceItem("mml_progress", "MML Progress")
    video_module_completion = ChoiceItem("video_module_completion", "Video Module Completion")
    assignment_module_completion = ChoiceItem("assignment_module_completion", "Assignment Module Completion")
    virtutor_session_completion = ChoiceItem("virtutor_session_completion", "Virtutor Session Completion")
    overtaking_peers = ChoiceItem("overtaking_peers", "Overtaking Peers")
    certification_path_completion = ChoiceItem("certification_path_completion", "Certification Path Completion")
    learning_path_completion = ChoiceItem("learning_path_completion", "Learning Path Completion")
    course_completion = ChoiceItem("course_completion", "Course Completion")

    @classmethod
    def get_milestone_category(cls, milestone_name):
        """Find the category of learning which the milestone belongs to."""

        from apps.my_learning.config import MilestoneCategoryTypeChoices

        if milestone_name in [
            cls.first_course_enroll,
            cls.first_course_complete,
            cls.course_self_enroll,
            cls.course_assigned,
            cls.module_completion_in_first_enrolled_course,
            cls.quick_finisher_self_enrolled_course,
            cls.quick_finisher_assigned_course,
            cls.course_certificate_earned,
            cls.course_completion,
        ]:
            category = MilestoneCategoryTypeChoices.course
        elif milestone_name in [
            cls.first_learning_path_enroll,
            cls.first_learning_path_complete,
            cls.learning_path_self_enroll,
            cls.learning_path_assigned,
            cls.quick_finisher_self_enrolled_lp,
            cls.quick_finisher_assigned_lp,
            cls.learning_path_starter,
            cls.learning_path_certificate_earned,
            cls.learning_path_completion,
        ]:
            category = MilestoneCategoryTypeChoices.learning_path
        elif milestone_name in [
            cls.first_certification_path_enrollment,
            cls.first_certification_path_completion,
            cls.certification_path_self_enrolled,
            cls.certification_path_assigned,
            cls.quick_finisher_self_enrolled_certification_path,
            cls.quick_finisher_assigned_certification_path,
            cls.certification_path_starter,
            cls.certification_path_certificate_earned,
            cls.certification_path_completion,
        ]:
            category = MilestoneCategoryTypeChoices.advanced_learning_path
        elif milestone_name in [
            cls.yaksha_completion,
        ]:
            category = MilestoneCategoryTypeChoices.assessment
        elif milestone_name in [
            cls.forum_post_creation,
            cls.forum_post_comments,
            cls.replying_comments,
        ]:
            category = MilestoneCategoryTypeChoices.forum
        else:
            category = "others"
        return category


MML_BADGES_RANGE = {
    "silver": {"from": 40, "to": 60},
    "gold": {"from": 61, "to": 80},
    "platinum": {"from": 81, "to": 100},
}


ASSESSMENT_BADGES_RANGE = {
    "silver": {"from": 60, "to": 75},
    "gold": {"from": 76, "to": 90},
    "platinum": {"from": 91, "to": 100},
}


class BadgeCategoryChoices(DjangoChoices):
    """Holds the choices of Badge Category types."""

    video = ChoiceItem("video", "Video")
    mml = ChoiceItem("mml", "MML")
    assessment = ChoiceItem("assessment", "Assessment")


class BadgeTypeChoices(DjangoChoices):
    """Holds the choices of Badge Types."""

    silver = ChoiceItem("silver", "Silver")
    gold = ChoiceItem("gold", "Gold")
    platinum = ChoiceItem("platinum", "Platinum")
    video = ChoiceItem("video", "Video")

    @classmethod
    def is_noble_metal(cls, value):
        """Value present in actual badges."""

        return value in [cls.silver, cls.gold, cls.platinum]


class BadgeLearningTypeChoices(DjangoChoices):
    """Choices for Badges learning model FKs."""

    course = ChoiceItem("course", "Course")
    learning_path = ChoiceItem("learning_path", "Learning Path")
    advanced_learning_path = ChoiceItem("advanced_learning_path", "Advanced Learning Path")
