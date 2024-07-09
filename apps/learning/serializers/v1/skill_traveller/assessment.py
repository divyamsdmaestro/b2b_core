from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import AssessmentProviderTypeChoices, AssessmentTypeChoices
from apps.learning.models import STAssessment
from apps.learning.serializers.v1 import BaseDependentCourseListSerializer


class STAssessmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the STAssessment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = STAssessment
        fields = [
            "name",
            "type",
            "provider_type",
            "st_course",
            "skill_traveller",
            "assessment_uuid",
        ]

    def validate(self, attrs):
        """Overridden to validate the assessment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == AssessmentTypeChoices.dependent_assessment and attrs["st_course"] is None:
            raise serializers.ValidationError({"st_course": "This field is required."})
        elif assignment_type == AssessmentTypeChoices.final_assessment and attrs["skill_traveller"] is None:
            raise serializers.ValidationError({"skill_traveller": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assessments."""

        if validated_data["type"] == AssessmentTypeChoices.final_assessment:
            last_instance = validated_data["skill_traveller"].related_st_assessments.order_by("-sequence").first()
        else:
            last_instance = validated_data["st_course"].related_st_assessments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {
            "type": self.serialize_dj_choices(AssessmentTypeChoices.choices),
            "provider_type": self.serialize_dj_choices(AssessmentProviderTypeChoices.choices),
        }


class STAssessmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the STAssessment."""

    st_course = BaseDependentCourseListSerializer(read_only=True)

    class Meta:
        model = STAssessment
        fields = [
            "id",
            "uuid",
            "name",
            "type",
            "provider_type",
            "st_course",
            "skill_traveller",
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
