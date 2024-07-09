from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import AssessmentProviderTypeChoices, AssessmentTypeChoices
from apps.learning.models import ALPAssessment


class ALPAssessmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the ALPAssessment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = ALPAssessment
        fields = [
            "name",
            "type",
            "provider_type",
            "alp_lp",
            "alp",
            "assessment_uuid",
        ]

    def validate(self, attrs):
        """Overridden to validate the assessment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == AssessmentTypeChoices.dependent_assessment and attrs["alp_lp"] is None:
            attrs["alp"] = None
            raise serializers.ValidationError({"alp_lp": "This field is required."})
        elif assignment_type == AssessmentTypeChoices.final_assessment and attrs["alp"] is None:
            attrs["alp_lp"] = None
            raise serializers.ValidationError({"alp": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assessments."""

        if validated_data["type"] == AssessmentTypeChoices.final_assessment:
            last_instance = validated_data["alp"].related_alp_assessments.order_by("-sequence").first()
        else:
            last_instance = validated_data["alp_lp"].related_alp_assessments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {
            "type": self.serialize_dj_choices(AssessmentTypeChoices.choices),
            "provider_type": self.serialize_dj_choices(AssessmentProviderTypeChoices.choices),
        }


class ALPAssessmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the ALPAssessment."""

    class Meta:
        model = ALPAssessment
        fields = [
            "id",
            "uuid",
            "name",
            "type",
            "provider_type",
            "alp_lp",
            "alp",
            "assessment_uuid",
            "sequence",
            "created_at",
        ]

    def get_filter_meta(self):
        """Returns filter metadata."""

        return {
            "type": self.serialize_dj_choices(AssessmentTypeChoices.choices),
            "provider_type": self.serialize_dj_choices(AssessmentProviderTypeChoices.choices),
        }
