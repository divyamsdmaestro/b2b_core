from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import STAssignment
from apps.learning.serializers.v1 import AssignmentListModelSerializer, BaseDependentCourseListSerializer


class STAssignmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the STAssignment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = STAssignment
        fields = ["type", "st_course", "skill_traveller", "assignment"]

    def validate(self, attrs):
        """Overridden to validate the assignment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == CommonLearningAssignmentTypeChoices.dependent_assignment and attrs["st_course"] is None:
            raise serializers.ValidationError({"st_course": "This field is required."})
        elif (
            assignment_type == CommonLearningAssignmentTypeChoices.final_assignment
            and attrs["skill_traveller"] is None
        ):
            raise serializers.ValidationError({"skill_traveller": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assignments."""

        if validated_data["type"] == CommonLearningAssignmentTypeChoices.final_assignment:
            last_instance = validated_data["skill_traveller"].related_st_assignments.order_by("-sequence").first()
        else:
            last_instance = validated_data["st_course"].related_st_assignments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {"type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices)}


class STAssignmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the STAssignment."""

    assignment = AssignmentListModelSerializer(read_only=True)
    st_course = BaseDependentCourseListSerializer(read_only=True)

    class Meta:
        model = STAssignment
        fields = [
            "id",
            "type",
            "st_course",
            "skill_traveller",
            "assignment",
            "sequence",
            "created_at",
        ]

    def get_filter_meta(self):
        """Returns filter metadata."""

        return {
            "type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices),
        }
