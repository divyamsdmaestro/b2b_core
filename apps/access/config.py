from djchoices import ChoiceItem, DjangoChoices


class GenderChoices(DjangoChoices):
    """Holds the choices of genders."""

    not_selected = ChoiceItem("prefer_not_to_say", "Prefer Not To Say")
    male = ChoiceItem("male", "Male")
    female = ChoiceItem("female", "Female")
    others = ChoiceItem("others", "Others")


class MaritalStatusChoices(DjangoChoices):
    """Holds the choices of Marital Status."""

    not_selected = ChoiceItem("prefer_not_to_say", "Prefer Not To Say")
    married = ChoiceItem("married", "Married")
    unmarried = ChoiceItem("unmarried", "Unmarried")


class UserConnectActionChoices(DjangoChoices):
    """Holds the choices of action."""

    follow = ChoiceItem("follow", "Follow")
    unfollow = ChoiceItem("unfollow", "Unfollow")
    add_friend = ChoiceItem("add_friend", "Add Friend")
    accept = ChoiceItem("accept", "Accept")
    reject = ChoiceItem("reject", "Reject")
