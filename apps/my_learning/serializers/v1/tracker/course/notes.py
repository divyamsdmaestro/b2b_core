from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.models import CourseSubModule
from apps.learning.serializers.v1.course.sub_module import CourseSubModuleListSerializer
from apps.my_learning.models import UserCourseNotes


class UserCourseNotesCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to add notes for sub_modules."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserCourseNotes
        fields = [
            "notes",
            "sub_module",
            "time_stamp",
        ]

    def validate(self, attrs):
        """Overriden to validate the user is enrolled in the learning or not."""

        sub_module = attrs["sub_module"]
        user = self.get_user()
        if not user.related_user_course_trackers.filter(course=sub_module.module.course):
            raise serializers.ValidationError({"sub_module": "Course not enrolled."})
        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        """Overridden to return the notes with sub_module details."""

        return UserCourseNotesListModelSerializer(instance).data

    def get_meta(self) -> dict:
        """Overridden to provide the submodule with name."""

        return {"sub_module": self.serialize_for_meta(CourseSubModule.objects.all(), fields=["id", "name"])}

    def update(self, instance, validated_data):
        """Overridden to validate the course is enrolled by a user or not."""

        sub_module = validated_data["sub_module"]
        course_tracker = sub_module.module.course.related_user_course_trackers.filter(user=self.get_user()).first()
        if not course_tracker:
            raise serializers.ValidationError({"sub_module": "Course not enrolled."})
        return super().update(instance, validated_data)


class UserCourseNotesListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the notes."""

    sub_module = CourseSubModuleListSerializer(read_only=True)

    class Meta:
        model = UserCourseNotes
        fields = [
            "id",
            "notes",
            "sub_module",
            "time_stamp",
        ]
