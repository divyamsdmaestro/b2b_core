from django.core import exceptions
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from rest_framework import serializers


@deconstructible
class MaxSizeValidator(BaseValidator):
    """Custom Max size validator for file fields."""

    message = ngettext_lazy(
        "Ensure this file has not more than %(limit_value)d MB.",
        "Ensure this file has not more than %(limit_value)d MB.",
        "limit_value",
    )
    code = "max_size"

    def compare(self, a, b):
        """Bytes to mb conversion and comparison between given input and default value."""

        a /= 1048576
        return a > b

    def clean(self, x):
        return len(x)


def validate_rating(value):
    """validate the course rating."""

    if value > 5:
        raise exceptions.ValidationError("Rating must be less than or equal to 5.")


def validate_pincode(value):
    """validate the pincode."""

    if value > 999999 or value <= 100000:  # check if it has 6 digits or not
        raise exceptions.ValidationError("Pincode must have only 6 digits.")


class ListUniqueValidator:
    """Validate the unique fields inside the request objects list."""

    message = {"default": _("This field must be unique.")}

    def __init__(self, unique_field_names, error_message=None):
        self.unique_field_names = unique_field_names
        self.message = error_message if error_message else self.message

    @staticmethod
    def has_duplicates(counter):
        return any([count for count in counter.values() if count > 1])

    def __call__(self, value):
        from collections import Counter

        field_counters = {
            field_name: Counter(item[field_name] for item in value if field_name in item)
            for field_name in self.unique_field_names
        }
        has_duplicates = any([ListUniqueValidator.has_duplicates(counter) for counter in field_counters.values()])
        if has_duplicates:
            errors = []
            for item in value:
                error = {}
                for field_name in self.unique_field_names:
                    counter = field_counters[field_name]
                    if counter[item.get(field_name)] > 1:
                        error.update(
                            {
                                field_name: self.message[field_name]
                                if field_name in self.message.keys()
                                else self.message["default"]
                            }
                        )
                errors.append(error)
            raise serializers.ValidationError(errors)

    def __repr__(self):
        return "<{}(unique_field_names={})>".format(
            self.__class__.__name__,
            self.unique_field_names,
        )
