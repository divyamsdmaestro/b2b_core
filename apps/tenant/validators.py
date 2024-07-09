import re
from string import ascii_letters, digits

from rest_framework import serializers


class DomainNameValidator:
    """
    Custom validator to validate a domain name.

    Usage:

    class MySerializer(serializers.Serializer):
        name = serializers.CharField(validators=[DomainNameValidator()])
    """

    def __call__(self, value):
        domain_pattern = r"^(?!:\/\/)(?!www\.)(?!.*-\.)(?!.*--\.)(?!.*\.\.)[a-zA-Z0-9-]{1,63}(?<!-)(\.[a-zA-Z]{2,})?$"

        if not bool(re.match(domain_pattern, value)):
            raise serializers.ValidationError("Invalid domain format. Please provide a valid Azure DNS domain.")


class DatabaseNameValidator:
    """Validate the database name."""

    def __call__(self, value):
        """Validate the database name."""

        value = f"{value}".strip()
        if any(char not in ascii_letters + digits + "_" for char in value):
            raise serializers.ValidationError("Name contains special characters.")
        if value.startswith("_"):
            raise serializers.ValidationError("Name should not starts with _")
        if value.endswith("_"):
            raise serializers.ValidationError("Name should not ends with _")
        if "__" in value:
            raise serializers.ValidationError("Name should not contains more than one _ in sequence.")
        return value
