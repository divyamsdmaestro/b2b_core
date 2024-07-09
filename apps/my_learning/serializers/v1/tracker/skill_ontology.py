from rest_framework import serializers

from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.learning.serializers.v1 import SkillOntologyListModelSerializer
from apps.my_learning.config import LearningStatusChoices
from apps.my_learning.models import UserSkillOntologyTracker
from apps.my_learning.serializers.v1 import UserBaseLearningRetrieveModelSerializer
from apps.my_learning.tasks import SkillOntologyProgressUpdateTask
from apps.tenant_service.middlewares import get_current_db_name


class UserSkillOntologyTrackerCreateSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to add the skill ontology tracker."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserSkillOntologyTracker
        fields = [
            "enrollment",
            "skill_ontology",
        ]

    def validate(self, attrs):
        """Overridden to check the enrolled course list."""

        enrollment_instance = attrs["enrollment"]
        user = self.get_user()
        if enrollment_instance.user != user and enrollment_instance.user_group not in user.related_user_groups.all():
            raise serializers.ValidationError({"enrollment": "Detail not found."})
        if user.related_user_skill_ontology_trackers.filter(skill_ontology=attrs["skill_ontology"]).first():
            raise serializers.ValidationError({"enrollment": "Already started."})
        return attrs

    def create(self, validated_data):
        """Create a tracker for course."""

        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        SkillOntologyProgressUpdateTask().run_task(db_name=get_current_db_name(), tracker_ids=[instance.id])
        return instance


class UserSkillOntologyRetrieveSerializer(SkillOntologyListModelSerializer, UserBaseLearningRetrieveModelSerializer):
    """Serializer class to retrieve the skill_ontology details."""

    class Meta(SkillOntologyListModelSerializer.Meta):
        fields = SkillOntologyListModelSerializer.Meta.fields + [
            "enrolled_details",
            "tracker_detail",
            "user_favourite",
        ]
