from djchoices import ChoiceItem, DjangoChoices


class WeekDayChoices(DjangoChoices):
    """Choices for days."""

    sunday = ChoiceItem("sunday", "Sunday")
    monday = ChoiceItem("monday", "Monday")
    tuesday = ChoiceItem("tuesday", "Tuesday")
    wednesday = ChoiceItem("wednesday", "Wednesday")
    thursday = ChoiceItem("thursday", "Thursday")
    friday = ChoiceItem("friday", "Friday")
    saturday = ChoiceItem("saturday", "Saturday")


class ActivityTypeChoices(DjangoChoices):
    """Choices for calendar activity type."""

    event = ChoiceItem("event", "Event")
    focus_time = ChoiceItem("focus_time", "Focus Time")


class CalendarEventTypeChoices(DjangoChoices):
    """Choices for calendar event type."""

    not_selected = ChoiceItem("not_selected", "Not Selected")
    session = ChoiceItem("session", "Session")
    course = ChoiceItem("course", "Course")
    learning_path = ChoiceItem("learning_path", "Learning Path")
    advanced_learning_path = ChoiceItem("advanced_learning_path", "Advanced Learning Path")
    lp_course = ChoiceItem("lp_course", "LP Course")
    alp_learning_path = ChoiceItem("alp_learning_path", "ALP Learning Path")


class RepeatTypeChoices(DjangoChoices):
    """Choices for calendar event repeat type."""

    does_not_repeat = ChoiceItem("does_not_repeat", "Does not repeat")
    daily = ChoiceItem("daily", "Daily")
    every_weekday = ChoiceItem("every_weekday", "Every Weekday (Monday to Friday)")
    custom = ChoiceItem("custom", "Custom")


class RepeatEveryTypeChoices(DjangoChoices):
    """Choices for repeat every types."""

    day = ChoiceItem("day", "Day")
    week = ChoiceItem("week", "Week")
    month = ChoiceItem("month", "Month")
    year = ChoiceItem("year", "Year")


class TimePeriodChoices(DjangoChoices):
    """Choices for Leaderboard"""

    day = ChoiceItem("day", "Day")
    month = ChoiceItem("month", "Month")
    year = ChoiceItem("year", "Year")


class EndTypeChoices(DjangoChoices):
    """Choices for activity ending."""

    never = ChoiceItem("never", "Never")
    on = ChoiceItem("on", "On")
    after = ChoiceItem("after", "After")


class UserStatusChoices(DjangoChoices):
    """Choices for user status."""

    busy = ChoiceItem("busy", "Busy")
    free = ChoiceItem("free", "Free")


class UserVisibilityChoices(DjangoChoices):
    """Choices for user visibility."""

    default_visibility = ChoiceItem("default_visibility", "Default Visibility")
    public = ChoiceItem("public", "Public")
    private = ChoiceItem("private", "Private")


class RemainderChoices(DjangoChoices):
    """Choices for Remainder or Notify me."""

    five_min_before = ChoiceItem(5, "5 minutes before")
    ten_min_before = ChoiceItem(10, "10 minutes before")
    fifteen_min_before = ChoiceItem(15, "15 minutes before")
    thirty_min_before = ChoiceItem(30, "30 minutes before")
    one_hour_before = ChoiceItem(60, "1 hour before")
    one_day_before = ChoiceItem(1440, "1 day before")
