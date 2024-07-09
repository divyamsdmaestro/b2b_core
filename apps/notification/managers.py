from apps.common.managers import BaseObjectManagerQuerySet


class NotificationObjectManagerQueryset(BaseObjectManagerQuerySet):
    """
    Custom QuerySet for Notification models.

    Usage on the model class -
        objects = NotificationObjectManagerQueryset.as_manager()

    Available methods -
        get_or_none, read, unread
    """

    def read(self):
        """Filter results based on is_read = True."""

        return self.filter(is_read=True)

    def unread(self):
        """Filter results based on is_read = False."""

        return self.filter(is_read=False)
