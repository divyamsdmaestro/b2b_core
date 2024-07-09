from djchoices import ChoiceItem, DjangoChoices


class SessionJoinMechanismChoices(DjangoChoices):
    """Holds the Session Join Mechanism's dynamic keys choices."""

    teams = ChoiceItem("1", "Teams")
    bbb = ChoiceItem("3", "BBB")
