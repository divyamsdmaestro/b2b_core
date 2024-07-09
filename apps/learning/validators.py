import os

from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.common.config import CUSTOM_ERRORS_MESSAGES


def draft_action(validated_data):
    """Function that used to change the active state when the data is draft."""

    draft = validated_data["is_draft"]

    validated_data["is_active"] = not draft
    return validated_data


def end_date_validation(attrs):
    """Custom validation to perform end_date > start_date"""

    start_date = attrs.get("start_date")
    end_date = attrs.get("end_date")

    if end_date and start_date and end_date < start_date:
        raise serializers.ValidationError(
            {"end_date": f"End date must be greater or equal to start date({start_date})."}
        )


def rating_field_validation(attrs):
    """Validate the rating field if is_rating_enabled is True."""

    if attrs.get("is_rating_enabled") and "rating" not in attrs:
        raise serializers.ValidationError({"rating": "This field is required"})


def forum_field_validation(attrs):
    """Validate the forum field if is_forum_enabled is True."""

    if attrs.get("is_forum_enabled") and ("forums" not in attrs or len(attrs["forums"]) == 0):
        raise serializers.ValidationError({"forums": "This field is required"})


def learning_type_field_validation(attrs):
    """Validate skill & role attributes based on the learning type"""

    required_error = "This field is required."

    learning_type = attrs.get("learning_type", None)
    skill = attrs.get("skill")
    role = attrs.get("role")

    if learning_type == "skill_based":
        if not skill:
            raise serializers.ValidationError({"skill": required_error})
    elif learning_type == "role_based":
        if not role:
            raise serializers.ValidationError({"role": required_error})
    else:
        return True
    return True


def course_lp_alp_validation(instance, courses=[], lp=[], alp=[]):
    """Validate the course, lp and alp are present in the instance course, lp and alp."""

    instance_courses = instance.related_courses.all()
    instance_lp = instance.related_learning_paths.all()
    instance_alp = instance.related_advanced_learning_paths.all()

    errors = {}
    error = [CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"]["does_not_exist"]]

    for course in courses:
        if course not in instance_courses:
            errors.update({"course": error})

    for leaning_path in lp:
        if leaning_path not in instance_lp:
            errors.update({"learning_path": error})

    for advanced_learning_path in alp:
        if advanced_learning_path not in instance_alp:
            errors.update({"advanced_learning_path": error})

    if errors:
        raise serializers.ValidationError(errors)


def assignment_file_extension(value):
    """validates the file extension."""

    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".pdf", ".doc", ".docx"]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def validate_file_extension(value):
    """validates the file extension."""

    ext = os.path.splitext(value.name)[1]
    valid_extensions = [
        # Files
        ".pdf",
        ".doc",
        ".docx",
        # Images
        ".jpg",
        ".png",
        ".xlsx",
        ".xls",
        # Video
        ".mp4",
        # Audio
        ".mp3",
        # Text Files
        ".oml",
        ".txt",
    ]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def allowed_file_ext_validator(value):
    """validates the file extension."""

    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".pdf", ".doc", ".docx", ".xlsx", ".xls", ".mp4", ".oml", ".txt"]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def validate_file_size(value):
    """Validates the file size not more than 1GB."""

    file_size = value.size / 1073741824
    if file_size > 1:
        raise ValidationError("File size not more than 1 GB")


def validate_scorm_file_size(value):
    """Validates the scorm file size is not more than 200 MB."""

    file_size = value.size / (1024 * 1024)  # Convert bytes to megabytes
    if file_size > 200:
        raise ValidationError("File size must not be more than 200 MB.")


def validate_zip_file(value):
    """validates the file extension is .zip or not."""

    if len(value.name) > 23:
        raise ValidationError("File name must be less than 20 characters.")
    if os.path.splitext(value.name)[1].lower() != ".zip":
        raise ValidationError("Unsupported file extension.")
    if value.content_type != "application/zip":
        raise ValidationError("Unsupported file type. Only zip files are allowed.")


class FileSizeValidator:
    """Common validation class for file size."""

    def __init__(self, size) -> None:
        self.max_size = size

    def __call__(self, value):
        """Validate the size of the file."""

        if value.size > self.max_size * 1024 * 1024:
            raise ValidationError(f"File size should not more than {self.max_size} MB")
        return value
