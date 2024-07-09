from rest_framework import serializers

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer, AppWriteOnlyModelSerializer
from apps.learning.models import AdvancedLearningPath, Course, LearningPath
from apps.virtutor.models import Trainer


class AssignTrainerCreateModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to assign trainers to course, lp & alp."""

    class _Serializer(AppSerializer):
        """Serializer class for trainer."""

        first_name = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
        last_name = serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
        trainer_id = serializers.IntegerField()
        skills = serializers.ListField()

    trainer = _Serializer(many=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Trainer
        fields = [
            "trainer",
            "course",
        ]


class TrainerListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for trainer list."""

    skills = serializers.SerializerMethodField()

    def get_skills(self, obj):
        """Returns the list of skills."""

        return obj.skills["skills"]

    class Meta:
        model = Trainer
        fields = [
            "id",
            "first_name",
            "last_name",
            "trainer_id",
            "skills",
        ]


class RemoveTrainerSerializer(AppSerializer):
    """Serializer class for removing trainer from course, lp & alp."""

    trainer = serializers.PrimaryKeyRelatedField(queryset=Trainer.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.active(), allow_null=True)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.active(), allow_null=True)
    alp = serializers.PrimaryKeyRelatedField(queryset=AdvancedLearningPath.objects.active(), allow_null=True)
