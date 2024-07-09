from rest_framework import serializers

from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSpecificImageFieldSerializer,
    AppWriteOnlyModelSerializer,
)
from apps.meta.config import FacultyTypeChoices
from apps.meta.models import Faculty


class FacultyCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for Faculty model CUD."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Faculty
        fields = [
            "name",
            "type",
            "faculty_image",
            "description",
            "rating",
            "no_of_students",
            "no_of_courses",
        ]

    def get_meta(self) -> dict:
        """Overridden to get faculty meta details."""

        return {"type": self.serialize_dj_choices(FacultyTypeChoices.choices)}


class FacultyListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the faculty."""

    type = serializers.DictField(source="get_faculty_type")
    faculty_image = AppSpecificImageFieldSerializer(read_only=True)

    class Meta:
        model = Faculty
        fields = [
            "id",
            "name",
            "type",
            "faculty_image",
            "description",
            "rating",
            "no_of_students",
            "no_of_courses",
        ]
