from djchoices import ChoiceItem, DjangoChoices


class BaseProficiencyChoices(DjangoChoices):
    """Holds the choices of proficiency levels."""

    basic = ChoiceItem("basic", "Basic")
    intermediate = ChoiceItem("intermediate", "Intermediate")
    advance = ChoiceItem("advance", "Advance")


class BadgeProficiencyChoices(BaseProficiencyChoices):
    """Holds the choices of proficiency levels."""

    comprehensive = ChoiceItem("comprehensive", "Comprehensive")
    certification = ChoiceItem("certification", "Certification")

    @classmethod
    def get_previous_choice(cls, value):
        """Get the previous lower choice value from the given value."""

        match value:
            case cls.intermediate:
                previous_value = cls.basic
            case cls.advance:
                previous_value = cls.intermediate
            case cls.comprehensive:
                previous_value = cls.advance
            case cls.certification:
                previous_value = cls.comprehensive
            case _:
                previous_value = None
        return previous_value


class ProficiencyChoices(BadgeProficiencyChoices):
    """Holds the choices of proficiency levels."""

    conversant = ChoiceItem("conversant", "Conversant")
    general = ChoiceItem("general", "General")


class BaseResourceTypeChoices(DjangoChoices):
    """Holds the type of resources."""

    video = ChoiceItem("video", "Video")
    file = ChoiceItem("file", "File")
    custom_url = ChoiceItem("custom_url", "Custom URL")


class SubModuleTypeChoices(BaseResourceTypeChoices):
    """Holds the type of sub modules."""

    scorm = ChoiceItem("scorm", "Scorm")
    file_submission = ChoiceItem("file_submission", "File Submission")


class CourseResourceTypeChoices(BaseResourceTypeChoices):
    """Holds the type of resources."""

    course_within_catalogue = ChoiceItem("course_within_catalogue", "Course within catalogue")


class LearningTypeChoices(DjangoChoices):
    """Holds the  learning type choices."""

    basic = ChoiceItem("basic", "Basic")
    role = ChoiceItem("role_based", "Role Based")
    skill = ChoiceItem("skill_based", "Skill Based")


class CommonLearningAssignmentTypeChoices(DjangoChoices):
    """Holds the assessment type choices."""

    dependent_assignment = ChoiceItem("dependent_assignment", "Dependent Assignment")
    final_assignment = ChoiceItem("final_assignment", "Final Assignment")


class AssessmentTypeChoices(DjangoChoices):
    """Holds the assessment type choices."""

    dependent_assessment = ChoiceItem("dependent_assessment", "Dependent Assessment")
    final_assessment = ChoiceItem("final_assessment", "Final Assessment")


class AssessmentProviderTypeChoices(DjangoChoices):
    """Holds the assessment provider types."""

    yaksha = ChoiceItem("yaksha", "Yaksha")
    wecp = ChoiceItem("wecp", "Wecp")


class AssessmentResultTypeChoices(DjangoChoices):
    """Holds the assessment result types."""

    type1 = ChoiceItem(1, "Do not show results to candidate")
    type2 = ChoiceItem(2, "Show detailed section and skill level score metrics to the candidate.")
    type3 = ChoiceItem(3, "Show only assessment level score metrics to the candidate.")
    type4 = ChoiceItem(4, "Redirect to the custom URL on submission of assessment.")


class SkillTravellerLearningTypeChoices(DjangoChoices):
    """Holds the skill traveller learning type choices."""

    travel_destinations = ChoiceItem("travel_destinations", "Travel Destinations")
    travel_landscapes = ChoiceItem("travel_landscapes", "Travel Landscapes")
    travel_journeys = ChoiceItem("travel_journeys", "Travel Journeys")


class JourneyTypeChoices(DjangoChoices):
    """Holds the journey type choices."""

    hiking = ChoiceItem("hiking", "Hiking")
    trekking = ChoiceItem("trekking", "Trekking")
    weekend_gateway = ChoiceItem("weekend_gateway", "Weekend Gateway")
    business_travel = ChoiceItem("business_travel", "Business Travel")
    event_trip = ChoiceItem("event_trip", "Event Trip")
    long_term_slow_travel = ChoiceItem("long_term_slow_travel", "Long Term Slow Travel")


class PlaygroundTypeChoices(DjangoChoices):
    """Holds the Playground type choices."""

    project = ChoiceItem("project", "Project")
    challenges = ChoiceItem("challenges", "Challenges")
    assignment = ChoiceItem("assignment", "Assignment")


class PlaygroundGuidanceChoices(DjangoChoices):
    """Holds the Playground Guidance choices."""

    guided = ChoiceItem("guided", "Guided")
    unguided = ChoiceItem("unguided", "Unguided")


class PlaygroundToolChoices(DjangoChoices):
    """Holds the Playground Tool type choices."""

    mml = ChoiceItem("mml", "MML")
    yaksha = ChoiceItem("yaksha", "Yaksha")
    codelabs = ChoiceItem("codelabs", "Codelabs")


class ExpertLearningTypeChoices(DjangoChoices):
    """Holds the  learning type choices for experts."""

    course = ChoiceItem("course", "Course")
    learning_path = ChoiceItem("learning_path", "Learning Path")
    advanced_learning_path = ChoiceItem("advanced_learning_path", "Advanced Learning Path")


class AssignmentTypeChoices(DjangoChoices):
    """Holds the assignment type choices."""

    project = ChoiceItem("project", "Project")
    assignment = ChoiceItem("assignment", "Assignment")
    challenges = ChoiceItem("challenges", "Challenges")


class LearningUpdateTypeChoices(DjangoChoices):
    """Holds the learning update type choices."""

    announcement = ChoiceItem("announcement", "Announcement")
    broadcast = ChoiceItem("broadcast", "Broadcast")
    notification = ChoiceItem("notification", "Notification")
    alert = ChoiceItem("alert", "Alert")


class EvaluationTypeChoices(DjangoChoices):
    """Holds the evaluation type choices."""

    evaluated = ChoiceItem("evaluated", "Evaluated")
    non_evaluated = ChoiceItem("non_evaluated", "Non Evaluated")


class SubmissionTypeChoices(DjangoChoices):
    """Holds the assignment submission type choices."""

    online = ChoiceItem("online_file_submission", "Online File Submission")
    on_paper = ChoiceItem("on_paper_submission", "On Paper Submission")
    observed = ChoiceItem("observed_in_person", "Observed In Person")


class AllowedFileNumberTypeChoices(DjangoChoices):
    """Holds the allowed file number."""

    single = ChoiceItem("single_file", "Single File")
    multiple = ChoiceItem("multiple_file", "Multiple File")


class AllowedFileExtensionChoices(DjangoChoices):
    """Holds the allowed file extension."""

    pdf = ChoiceItem("pdf", "PDF")
    doc = ChoiceItem("doc", "DOC")
    docx = ChoiceItem("docx", "DOCX")
    html = ChoiceItem("html", "HTML")
    xls = ChoiceItem("xls", "XLS")
    xlsx = ChoiceItem("xlsx", "XLSX")
    txt = ChoiceItem("txt", "TXT")
    zip = ChoiceItem("zip", "ZIP")


class AllowedSubmissionChoices(DjangoChoices):
    """Allowed submission type choices."""

    all = ChoiceItem("all", "All submissions are allowed")
    one = ChoiceItem("one", "Only one submission allowed")
    recent = ChoiceItem("recent", "Only the most recent submission is allowed")


class BaseUploadStatusChoices(DjangoChoices):
    """Holds the status of uploads."""

    # Any change here should not affect DBRouter table. Or create another class for DBRouter.
    initiated = ChoiceItem("initiated", "Initiated")
    in_progress = ChoiceItem("in_progress", "In Progress")
    completed = ChoiceItem("completed", "Completed")
    failed = ChoiceItem("failed", "Failed")


class AssignmentGuidanceChoices(DjangoChoices):
    """Holds the Assignment Guidance choices."""

    guided = ChoiceItem("guided", "Guided")
    unguided = ChoiceItem("unguided", "Unguided")
