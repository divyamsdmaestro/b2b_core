from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel
from apps.notification.config import NotifyActionChoices
from apps.notification.managers import NotificationObjectManagerQueryset


class Notification(BaseModel):
    """
    Model to Store User's In-App Notifications.

    ********************* Model Fields *********************

        PK          - id,
        FK          - user,
        Fields      - message, data, is_read
        Datetime    - read_at, created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none, read, unread
    """

    class Meta(BaseModel.Meta):
        default_related_name = "related_notifications"

    # QS Manager
    objects = NotificationObjectManagerQueryset.as_manager()

    # FK Fields
    user = models.ForeignKey("access.User", on_delete=models.CASCADE)
    # Fields
    message = models.TextField()
    data = models.JSONField(default=dict)
    read_at = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        """Message as string rep."""

        return self.message

    @classmethod
    def notify_user(cls, user, action, **kwargs):
        """Create Notification for user based on action."""

        message, data = cls.notify_details(action, **kwargs)
        return cls.objects.create(user=user, message=message, data=data)

    @staticmethod
    def notify_details(action, **kwargs):
        """Return appropriate notify message and include additional details in data."""

        data = {"action": action, **kwargs}
        obj_name = kwargs.get("obj_name", None)
        match action:
            # course
            case NotifyActionChoices.self_course_enroll:
                data["course_id"] = kwargs.get("course_id", None)
                message = f"You have self enrolled to {obj_name} course successfully."
            case NotifyActionChoices.course_assigned:
                data["course_id"] = kwargs.get("course_id", None)
                message = f"Course {obj_name} has been assigned to you."
            case NotifyActionChoices.course_complete:
                data["course_id"] = kwargs.get("course_id", None)
                message = f"You have successfully completed the course {obj_name}."
            # LP
            case NotifyActionChoices.self_lp_enroll:
                data["learning_path_id"] = kwargs.get("learning_path_id", None)
                message = f"You have self enrolled to {obj_name} learning path successfully."
            case NotifyActionChoices.lp_assigned:
                data["learning_path_id"] = kwargs.get("learning_path_id", None)
                message = f"Learning Path {obj_name} has been assigned to you."
            case NotifyActionChoices.lp_complete:
                data["learning_path_id"] = kwargs.get("learning_path_id", None)
                message = f"You have successfully completed the learning path {obj_name}."
            # ALP
            case NotifyActionChoices.self_alp_enroll:
                data["advanced_learning_path_id"] = kwargs.get("advanced_learning_path_id", None)
                message = f"You have self enrolled to {obj_name} advanced learning path successfully."
            case NotifyActionChoices.alp_assigned:
                data["advanced_learning_path_id"] = kwargs.get("advanced_learning_path_id", None)
                message = f"Advanced Learning Path {obj_name} has been assigned to you."
            case NotifyActionChoices.alp_complete:
                data["advanced_learning_path_id"] = kwargs.get("advanced_learning_path_id", None)
                message = f"You have successfully completed the advanced learning path {obj_name}."
            # Skill Ontology
            case NotifyActionChoices.skill_ontology_enroll:
                data["skill_ontology_id"] = kwargs.get("skill_ontology_id", None)
                message = f"You have enrolled to {obj_name} skill ontology successfully."
            case NotifyActionChoices.skill_ontology_complete:
                data["skill_ontology_id"] = kwargs.get("skill_ontology_id", None)
                message = f"You have successfully completed the skill ontology {obj_name}."
            case _:
                raise ValueError("Invalid Notification Type")
        return message, data
