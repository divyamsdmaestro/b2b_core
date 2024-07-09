from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import AssessmentProviderTypeChoices, AssessmentTypeChoices
from apps.learning.models import CourseAssessment


class CourseAssessmentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create, update & delete the CourseAssessment."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = CourseAssessment
        fields = [
            "name",
            "type",
            "provider_type",
            "module",
            "course",
            "assessment_uuid",
        ]

    def validate(self, attrs):
        """Overridden to validate the assessment type & related fields."""

        assignment_type = attrs.get("type")
        if assignment_type == AssessmentTypeChoices.dependent_assessment and attrs["module"] is None:
            attrs["course"] = None
            raise serializers.ValidationError({"module": "This field is required."})
        elif assignment_type == AssessmentTypeChoices.final_assessment and attrs["course"] is None:
            attrs["module"] = None
            raise serializers.ValidationError({"course": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence of assessments."""

        if validated_data["type"] == AssessmentTypeChoices.final_assessment:
            last_instance = validated_data["course"].related_course_assessments.order_by("-sequence").first()
        else:
            last_instance = validated_data["module"].related_course_assessments.order_by("-sequence").first()
        validated_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
        return super().create(validated_data)

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {
            "type": self.serialize_dj_choices(AssessmentTypeChoices.choices),
            "provider_type": self.serialize_dj_choices(AssessmentProviderTypeChoices.choices),
        }


class CourseAssessmentListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the CourseAssessment."""

    class Meta:
        model = CourseAssessment
        fields = [
            "id",
            "uuid",
            "name",
            "type",
            "provider_type",
            "module",
            "course",
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
