from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import AssessmentProviderTypeChoices, AssessmentTypeChoices
from apps.learning.models import LPAssessment
from apps.learning.serializers.v1 import BaseDependentCourseListSerializer


class LPAssessmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the LPAssessment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = LPAssessment
        fields = [
            "name",
            "type",
            "provider_type",
            "lp_course",
            "learning_path",
            "assessment_uuid",
        ]

    def validate(self, attrs):
        """Overridden to validate the assessment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == AssessmentTypeChoices.dependent_assessment and attrs["lp_course"] is None:
            attrs["learning_path"] = None
            raise serializers.ValidationError({"lp_course": "This field is required."})
        elif assignment_type == AssessmentTypeChoices.final_assessment and attrs["learning_path"] is None:
            attrs["lp_course"] = None
            raise serializers.ValidationError({"learning_path": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assessments."""

        if validated_data["type"] == AssessmentTypeChoices.final_assessment:
            last_instance = validated_data["learning_path"].related_lp_assessments.order_by("-sequence").first()
        else:
            last_instance = validated_data["lp_course"].related_lp_assessments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {
            "type": self.serialize_dj_choices(AssessmentTypeChoices.choices),
            "provider_type": self.serialize_dj_choices(AssessmentProviderTypeChoices.choices),
        }


class LPAssessmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the LPAssessment."""

    lp_course = BaseDependentCourseListSerializer(read_only=True)

    class Meta:
        model = LPAssessment
        fields = [
            "id",
            "uuid",
            "name",
            "type",
            "provider_type",
            "lp_course",
            "learning_path",
            "assessment_uuid",
            "sequence",
            "created_at",
            "is_practice",
        ]

    def get_filter_meta(self):
        """Returns filter metadata."""

        return {
            "type": self.serialize_dj_choices(AssessmentTypeChoices.choices),
            "provider_type": self.serialize_dj_choices(AssessmentProviderTypeChoices.choices),
        }
