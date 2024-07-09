from djchoices import ChoiceItem, DjangoChoices


class ForumTypeChoices(DjangoChoices):
    """Holds the choices of forum types."""

    public = ChoiceItem("public", "Public")
    private = ChoiceItem("private", "Private")
    course = ChoiceItem("course", "Course")


class PostTypeChoices(DjangoChoices):
    """Holds the choices of post types."""

    question_based = ChoiceItem("question_based", "Question based")
    poll_based = ChoiceItem("poll_based", "Poll Based")
