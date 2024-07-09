from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import CommonLearningAssignmentTypeChoices
from apps.learning.models import ALPAssignment
from apps.learning.serializers.v1 import AssignmentListModelSerializer


class ALPAssignmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the ALPAssignment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = ALPAssignment
        fields = ["type", "alp_lp", "alp", "assignment"]

    def validate(self, attrs):
        """Overridden to validate the assignment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == CommonLearningAssignmentTypeChoices.dependent_assignment and attrs["alp_lp"] is None:
            attrs["alp"] = None
            raise serializers.ValidationError({"alp_lp": "This field is required."})
        elif assignment_type == CommonLearningAssignmentTypeChoices.final_assignment and attrs["alp"] is None:
            attrs["alp_lp"] = None
            raise serializers.ValidationError({"alp": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assignments."""

        if validated_data["type"] == CommonLearningAssignmentTypeChoices.final_assignment:
            last_instance = validated_data["alp"].related_alp_assignments.order_by("-sequence").first()
        else:
            last_instance = validated_data["alp_lp"].related_alp_assignments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {"type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices)}


class ALPAssignmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the ALPAssignment."""

    assignment = AssignmentListModelSerializer(read_only=True)

    class Meta:
        model = ALPAssignment
        fields = [
            "id",
            "type",
            "alp_lp",
            "alp",
            "assignment",
            "sequence",
            "created_at",
        ]

    def get_filter_meta(self):
        """Returns filter metadata."""

        return {
            "type": self.serialize_dj_choices(CommonLearningAssignmentTypeChoices.choices),
        }
