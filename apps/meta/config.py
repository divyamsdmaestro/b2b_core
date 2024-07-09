from djchoices import ChoiceItem, DjangoChoices


class FacultyTypeChoices(DjangoChoices):
    """Choices for faculty type."""

    author = ChoiceItem("author", "Author")
    instructor = ChoiceItem("instructor", "Instructor")


class FeedBackTypeChoices(DjangoChoices):
    """Choices for Feedback Type `Choice/Text`"""

    choice = ChoiceItem("choice", "Choice")
    text = ChoiceItem("text", "Text")
