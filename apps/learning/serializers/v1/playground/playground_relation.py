from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.models import PlaygroundRelationModel
from apps.learning.serializers.v1 import PlaygroundGroupListSerializer, PlaygroundListModelSerializer


class PlaygroundRelationModelRetrieveSerializer(AppReadOnlyModelSerializer):
    """Serializer class to retrieve list of playgrounds in a playground group list."""

    playground = PlaygroundListModelSerializer(read_only=True)
    playground_group = PlaygroundGroupListSerializer(read_only=True)

    class Meta:
        model = PlaygroundRelationModel
        fields = [
            "id",
            "playground",
            "playground_group",
            "sequence",
            "is_mandatory",
        ]


class PlaygroundAllocationCUDSerializer(AppWriteOnlyModelSerializer):
    """PlaygroundRelation CRUD serializer."""

    class Meta(AppCreateModelSerializer.Meta):
        model = PlaygroundRelationModel
        fields = [
            "playground",
            "sequence",
            "playground_group",
            "is_mandatory",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validation."""

        playground, playground_group, sequence = attrs["playground"], attrs["playground_group"], attrs["sequence"]

        if not self.instance:
            playground_relation = playground_group.related_playground_relations.all()
            if playground_relation.filter(playground=playground).first():
                raise serializers.ValidationError({"playground": "Playground is already present."})
            if playground_relation.filter(sequence=sequence).first():
                raise serializers.ValidationError({"sequence": "This sequence is already allocated."})
        else:
            playground_relations = playground_group.related_playground_relations.all().exclude(id=self.instance.id)
            playground_sequence_list = playground_relations.values_list("sequence", flat=True)
            if sequence in playground_sequence_list:
                raise serializers.ValidationError({"sequence": "This sequence is already allocated."})
        return attrs
