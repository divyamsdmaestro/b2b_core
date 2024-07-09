from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import LPAssignment
from apps.learning.serializers.v1 import AssignmentListModelSerializer, BaseDependentCourseListSerializer


class LPAssignmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the LPAssignment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = LPAssignment
        fields = ["type", "lp_course", "learning_path", "assignment"]

    def validate(self, attrs):
        """Overridden to validate the assignment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == CommonLearningAssignmentTypeChoices.dependent_assignment and attrs["lp_course"] is None:
            attrs["learning_path"] = None
            raise serializers.ValidationError({"lp_course": "This field is required."})
        elif (
            assignment_type == CommonLearningAssignmentTypeChoices.final_assignment and attrs["learning_path"] is None
        ):
            attrs["lp_course"] = None
            raise serializers.ValidationError({"learning_path": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assignments."""

        if validated_data["type"] == CommonLearningAssignmentTypeChoices.final_assignment:
            last_instance = validated_data["learning_path"].related_lp_assignments.order_by("-sequence").first()
        else:
            last_instance = validated_data["lp_course"].related_lp_assignments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {"type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices)}


class LPAssignmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the LPAssignment."""

    assignment = AssignmentListModelSerializer(read_only=True)
    lp_course = BaseDependentCourseListSerializer(read_only=True)

    class Meta:
        model = LPAssignment
        fields = [
            "id",
            "type",
            "lp_course",
            "learning_path",
            "assignment",
            "sequence",
            "created_at",
        ]

    def get_filter_meta(self):
        """Returns filter metadata."""

        return {
            "type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices),
        }
