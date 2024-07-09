from django.utils import timezone
from rest_framework import serializers

from apps.access.models import UserSkillDetail
from apps.access.serializers.v1 import UserSkillDetailCreateSerializer, UserSkillDetailRetrieveSerializer
from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer
from apps.learning.config import ProficiencyChoices
from apps.learning.models import (
    AdvancedLearningPath,
    Assignment,
    AssignmentGroup,
    Course,
    LearningPath,
    SkillOntology,
    SkillTraveller,
)
from apps.my_learning.config import ActionChoices, ApprovalTypeChoices, EnrollmentTypeChoices

SKILL_ONTOLOGY_FIELDS = [
    "name",
    "current_skill_detail",
    "desired_skill_detail",
    "course",
    "learning_path",
    "advanced_learning_path",
    "skill_traveller",
    "assignment",
    "assignment_group",
]


class SkillOntologyListModelSerializer(AppReadOnlyModelSerializer):
    """SkillOntology List serializer."""

    current_skill_detail = UserSkillDetailRetrieveSerializer(read_only=True)
    desired_skill_detail = UserSkillDetailRetrieveSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = SkillOntology
        fields = SKILL_ONTOLOGY_FIELDS + ["id"]


class SkillOntologyCreateSerializer(AppCreateModelSerializer):
    """Serializer class to create skill ontology."""

    current_skill_detail = UserSkillDetailCreateSerializer()
    desired_skill_detail = UserSkillDetailCreateSerializer()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.active(), many=True)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.active(), many=True)
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.active(), many=True
    )
    skill_traveller = serializers.PrimaryKeyRelatedField(queryset=SkillTraveller.objects.active(), many=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.active(), many=True)
    assignment_group = serializers.PrimaryKeyRelatedField(queryset=AssignmentGroup.objects.active(), many=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = SkillOntology
        fields = SKILL_ONTOLOGY_FIELDS

    def create_skill_detail(self, skill, proficiency):
        """Function to create a user skill detail for a given skill and proficiency."""

        if obj := UserSkillDetail.objects.filter(skill=skill, proficiency=proficiency):
            return obj.first()
        instance = UserSkillDetail.objects.create(skill=skill, proficiency=proficiency)
        return instance

    def create(self, validated_data):
        """Overridden to update the count of various learning items."""

        user = self.get_user()
        validated_data["user"] = user
        current_skill = validated_data.pop("current_skill_detail")
        desired_skill = validated_data.pop("desired_skill_detail")
        instance = super().create(validated_data=validated_data)
        instance.current_skill_detail = self.create_skill_detail(current_skill["skill"], current_skill["proficiency"])
        instance.desired_skill_detail = self.create_skill_detail(desired_skill["skill"], desired_skill["proficiency"])
        instance.save(update_fields=["current_skill_detail", "desired_skill_detail"])
        enrollment_args = {
            "created_by": user,
            "action": ActionChoices.approved,
            "action_date": timezone.now().date(),
            "reason": "Self Enrolled",
            "actionee_id": user.id,
            "approval_type": ApprovalTypeChoices.self_enrolled,
            "is_enrolled": True,
            "learning_type": EnrollmentTypeChoices.skill_ontology,
            "skill_ontology_id": instance.id,
        }
        enrollment = user.related_enrollments.create(**enrollment_args)
        enrollment.notify_user()
        return instance

    def get_meta(self) -> dict:
        """Returns meta data."""

        return {
            "proficiency": self.serialize_dj_choices(ProficiencyChoices.choices),
        }
