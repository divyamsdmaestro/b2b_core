from django.utils import timezone
from rest_framework import serializers


class VirtutorStartDateValidator:
    """
    Custom validator to validate a date greater than current time.

    Usage:

    class MySerializer(serializers.Serializer):
        name = serializers.DateTimeField(validators=[VirtutorStartDateValidator()])
    """

    def __call__(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("DateTime must be greater than current time.")
