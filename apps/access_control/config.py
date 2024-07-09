from djchoices import ChoiceItem, DjangoChoices


class RoleTypeChoices(DjangoChoices):
    """Choices for user roles."""

    admin = ChoiceItem("admin", "Admin")
    manager = ChoiceItem("manager", "Manager")
    learner = ChoiceItem("learner", "Learner")
    author = ChoiceItem("author", "Author")
