from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.models import AssignmentGroup, AssignmentRelation
from apps.learning.serializers.v1 import (
    AssignmentListModelSerializer,
    BaseAssignmentCUDModelSerializer,
    BaseAssignmentRetrieveModelSerializer,
    BaseLearningListModelSerializer,
)


class AssignmentGroupListSerializer(BaseLearningListModelSerializer):
    """Assignment group retrieve model serializer."""

    class Meta(BaseLearningListModelSerializer.Meta):
        model = AssignmentGroup
        fields = BaseLearningListModelSerializer.Meta.fields + ["no_of_assignments"]


class AssignmentGroupRetrieveSerializer(BaseAssignmentRetrieveModelSerializer):
    """Assignment group retrieve model serializer."""

    class Meta(BaseAssignmentRetrieveModelSerializer.Meta):
        model = AssignmentGroup
        fields = BaseAssignmentRetrieveModelSerializer.Meta.fields + [
            "no_of_assignments",
        ]


class AssignmentGroupCUDModelSerializer(BaseAssignmentCUDModelSerializer):
    """Serializer class to create Assignment Group."""

    class Meta(BaseAssignmentCUDModelSerializer.Meta):
        model = AssignmentGroup
        fields = BaseAssignmentCUDModelSerializer.Meta.fields


class AssignmentRelationListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to retrieve list of assignments in a assignment group list."""

    assignment = AssignmentListModelSerializer(read_only=True)
    assignment_group = BaseIDNameSerializer(read_only=True)

    class Meta:
        model = AssignmentRelation
        fields = [
            "id",
            "assignment",
            "assignment_group",
            "sequence",
            "is_mandatory",
        ]


class AssignmentAllocationCUDSerializer(AppWriteOnlyModelSerializer):
    """AssignmentRelation CRUD serializer."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = AssignmentRelation
        fields = [
            "assignment",
            "assignment_group",
            "is_mandatory",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validation."""

        assignment, assignment_group = attrs["assignment"], attrs["assignment_group"]
        if not self.instance and assignment_group.related_assignment_relations.filter(assignment=assignment):
            raise serializers.ValidationError({"assignment": "Assignment is already present."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence, duration & count."""

        assignment_group = validated_data["assignment_group"]
        max_position = (
            assignment_group.related_assignment_relations.order_by("-sequence")
            .values_list("sequence", flat=True)
            .first()
        )
        validated_data["sequence"] = max_position + 1 if max_position else 1
        instance = super().create(validated_data)
        instance.assignment_group.duration_and_count_update()
        return instance
