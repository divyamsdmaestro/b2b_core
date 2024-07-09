from datetime import datetime

from rest_framework import serializers

from apps.common.serializers import AppSerializer
from apps.learning.models import (
    AdvancedLearningPath,
    Assignment,
    AssignmentGroup,
    Course,
    LearningPath,
    SkillTraveller,
)
from apps.my_learning.config import AllBaseLearningTypeChoices


class LearningRetireSerializer(AppSerializer):
    """Serializer class for make the learnings retired."""

    learning_type = serializers.ChoiceField(choices=AllBaseLearningTypeChoices.choices, required=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive(), required=False, allow_null=True)
    learning_path = serializers.PrimaryKeyRelatedField(
        queryset=LearningPath.objects.alive(), required=False, allow_null=True
    )
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.alive(), required=False, allow_null=True
    )
    skill_traveller = serializers.PrimaryKeyRelatedField(
        queryset=SkillTraveller.objects.alive(), required=False, allow_null=True
    )
    assignment = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.alive(), required=False, allow_null=True
    )
    assignment_group = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentGroup.objects.alive(), required=False, allow_null=True
    )
    retirement_date = serializers.DateField(required=True, allow_null=True)
    is_retired = serializers.BooleanField(required=False)

    def validate(self, attrs):
        """Overridden to validate the necessary fields."""

        learning_type = attrs.get("learning_type")
        retirement_date = attrs["retirement_date"]
        instance = attrs.get(learning_type)
        if not instance:
            raise serializers.ValidationError({learning_type: "This field is required"})
        if attrs.get("is_retired", True) and instance.is_retired:
            raise serializers.ValidationError({learning_type: "This course is already retired."})
        if retirement_date and retirement_date < datetime.today().date():
            raise serializers.ValidationError({"retirement_date": "Date must be greated than or equal to today."})
        attrs["instance"] = instance
        return attrs
