from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.db.models import QuerySet
from django.utils import timezone


class BaseObjectManagerQuerySet(QuerySet):
    """
    The main/base manager for the apps models. This is used for including common
    model filters and methods. This is used just to make things DRY.

    This can be used in both ways:
        1. Model.app_objects.custom_method()
        2. Model.app_objects.filter().custom_method()

    Usage on the model class -
        objects = BaseObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
    """

    def get_or_none(self, *args, **kwargs):
        """
        Get the object based on the given **kwargs. If not present returns None.
        Note: Expects a single instance.
        """

        try:
            return self.get(*args, **kwargs)
        # if it does not exist or if idiotic values like id=None is passed
        except (
            ObjectDoesNotExist,
            AttributeError,
            ValueError,
            MultipleObjectsReturned,
            ValidationError,  # invalid UUID
        ):
            return None


class StatusModelObjectManagerQuerySet(BaseObjectManagerQuerySet):
    """
    Custom QuerySet for Status Models.

    Usage on the model class -
        objects = StatusModelObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
        active
        inactive
    """

    def active(self):
        """
        Return a queryset of only the active objects, which have `is_active`.
        set to True.
        """

        return self.filter(is_active=True)

    def inactive(self):
        """
        Return a queryset of only the inactive objects, which have `is_active`
        set to False.
        """

        return self.filter(is_active=False)


class SoftDeleteObjectManagerQuerySet(BaseObjectManagerQuerySet):
    """
    Custom QuerySet for soft-deletable models.

    Usage on the model class -
        objects = SoftDeleteObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
        alive
        dead
        delete
        hard_delete
    """

    def alive(self):
        """
        Return a queryset of only the non-soft-deleted objects, which have
        `is_deleted` set to False.
        """

        return self.filter(is_deleted=False)

    def dead(self):
        """
        Return a queryset of only the soft-deleted objects, which have
        `is_deleted` set to True.
        """

        return self.filter(is_deleted=True)

    def delete(self):
        """
        Soft-delete the queryset by updating `is_deleted` and `is_active`
        fields to True and False respectively.
        """

        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """
        Hard-delete the queryset by calling the default `delete` method
        of the queryset.
        """

        return super().delete()


class ArchivableObjectManagerQuerySet(SoftDeleteObjectManagerQuerySet):
    """
    Custom QuerySet for soft-deletable and Status tracking models that inherits from
    `SoftDeleteObjectManagerQuerySet`.

    Usage on the model class -
        objects = ArchivableObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
        active,
        inactive,
        alive,
        dead,
        delete,
        hard_delete
    """

    def active(self):
        """
        Overridden to set archivable fields. Return a queryset of only the active objects, which have `is_active`
        set to True and `is_deleted` set to False.
        """

        return self.filter(is_active=True, is_deleted=False)

    def inactive(self):
        """
        Overridden to set archivable fields. Return a queryset of only the inactive objects, which have `is_active`
        set to False and `is_deleted` set to False.
        """

        return self.filter(is_active=False, is_deleted=False)

    def delete(self):
        """
        Overridden to set archivable fields. Soft-delete the queryset by updating `is_deleted` and `is_active`
        fields to True and False respectively.
        """

        return super().update(is_deleted=True, is_active=False, deleted_at=timezone.now())


class CourseSkeletonObjectManagerQuerySet(ArchivableObjectManagerQuerySet):
    """
    Custom QuerySet for archivable models that inherits from `ArchivableObjectManagerQuerySet`.

    Usage on the model class -
        objects = CourseSkeletonObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
        active,
        inactive,
        alive,
        dead,
        delete,
        hard_delete,
        unarchived,
    """

    def unarchived(self):
        """
        Return a queryset of only the unarchived objects, which have `is_archive` set to False.
        """

        return self.filter(is_archive=False, is_active=True, is_deleted=False)
