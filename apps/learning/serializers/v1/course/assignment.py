from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import CourseAssignment
from apps.learning.serializers.v1 import AssignmentListModelSerializer


class CourseAssignmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """CUD Serializer for course module assignments."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = CourseAssignment
        fields = [
            "type",
            "module",
            "course",
            "assignment",
        ]

    def validate(self, attrs):
        """Overridden to validate the assignment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == CommonLearningAssignmentTypeChoices.dependent_assignment and attrs["module"] is None:
            attrs["course"] = None
            raise serializers.ValidationError({"module": "This field is required."})
        elif assignment_type == CommonLearningAssignmentTypeChoices.final_assignment and attrs["course"] is None:
            attrs["module"] = None
            raise serializers.ValidationError({"course": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assignments."""

        if validated_data["type"] == CommonLearningAssignmentTypeChoices.final_assignment:
            last_instance = validated_data["course"].related_course_assignments.order_by("-sequence").first()
        else:
            last_instance = validated_data["module"].related_course_assignments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {"type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices)}


class CourseAssignmentListModelSerializer(AppReadOnlyModelSerializer):
    """List serializer for module assignments."""

    assignment = AssignmentListModelSerializer(read_only=True)

    class Meta:
        model = CourseAssignment
        fields = [
            "id",
            "uuid",
            "type",
            "module",
            "course",
            "assignment",
            "sequence",
            "created_at",
        ]

    def get_filter_meta(self):
        """Returns filter metadata."""

        return {
            "type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices),
        }
