from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.learning.config import LearningTypeChoices
from apps.learning.models import LearningPath, LearningPathCourse, LearningPathResource
from apps.learning.serializers.v1 import (
    BaseLearningListModelSerializer,
    BaseLearningSkillRoleCUDModelSerializer,
    BaseLearningSkillRoleRetrieveModelSerializer,
    CommonResourceCreateModelSerializer,
    CommonResourceListModelSerializer,
    CourseListModelSerializer,
)
from apps.learning.validators import learning_type_field_validation


class LearningPathCUDModelSerializer(BaseLearningSkillRoleCUDModelSerializer):
    """Learning path CUD serializer"""

    class Meta(BaseLearningSkillRoleCUDModelSerializer.Meta):
        model = LearningPath
        fields = BaseLearningSkillRoleCUDModelSerializer.Meta.fields + [
            "learning_type",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validations"""

        attrs = super().validate(attrs)
        learning_type_field_validation(attrs)
        return attrs

    def create(self, validated_data):
        """Overridden to change the active field when the data to be save as draft."""

        validated_data["is_active"] = False
        instance = super().create(validated_data=validated_data)
        instance.role.all().role_learning_path_count_update()
        instance.skill.all().skill_learning_path_count_update()
        instance.category.category_learning_path_count_update()
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the skill, role& category learning_path count & the draft field to instance."""

        instance = super().update(instance=instance, validated_data=validated_data)
        instance.role.all().role_learning_path_count_update()
        instance.skill.all().skill_learning_path_count_update()
        instance.category.category_learning_path_count_update()
        return instance

    def get_meta(self) -> dict:
        """Get meta & initial values for learning_paths."""

        metadata = super().get_meta()
        metadata["learning_type"] = self.serialize_dj_choices(LearningTypeChoices.choices)
        return metadata


class LearningPathListModelSerializer(BaseLearningListModelSerializer):
    """Learning path retrieve model serializer."""

    skill = serializers.SerializerMethodField(read_only=True)

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    class Meta(BaseLearningListModelSerializer.Meta):
        model = LearningPath
        fields = BaseLearningListModelSerializer.Meta.fields + ["skill", "no_of_courses"]

    def get_filter_meta(self):
        """Return the filter meta."""

        data = super().get_filter_meta()
        data["learning_type"] = self.serialize_dj_choices(LearningTypeChoices.choices)
        return data


class LearningPathRetrieveModelSerializer(BaseLearningSkillRoleRetrieveModelSerializer):
    """Learning path retrieve model serializer."""

    class Meta(BaseLearningSkillRoleRetrieveModelSerializer.Meta):
        model = LearningPath
        fields = BaseLearningSkillRoleRetrieveModelSerializer.Meta.fields + [
            "learning_type",
            "no_of_courses",
        ]


class LPCourseListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to retrieve list of learning_path_courses list."""

    course = CourseListModelSerializer(read_only=True)

    class Meta:
        model = LearningPathCourse
        fields = [
            "id",
            "course",
            "learning_path",
            "sequence",
            "course_unlock_date",
            "is_mandatory",
            "is_locked",
        ]


class LPCourseAllocationCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for assign the courses to learning paths."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = LearningPathCourse
        fields = [
            "learning_path",
            "course",
            "course_unlock_date",
            "is_mandatory",
            "is_locked",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validation."""

        course, lp = attrs["course"], attrs["learning_path"]
        is_locked, unlock_date = attrs["is_locked"], attrs["course_unlock_date"]
        lp_course = lp.related_learning_path_courses.all()
        if self.instance:
            lp_course = lp_course.exclude(id=self.instance.id)
        if lp_course.filter(course=course).first():
            raise serializers.ValidationError({"course": "Course is already present in this Learning Path."})
        if is_locked and (not lp.start_date or not lp.end_date):
            msg = "This Learning Path doesn't have start date and end date specified. Hence course cannot be locked."
            raise serializers.ValidationError({"course_unlock_date": msg})
        if is_locked and not unlock_date:
            raise serializers.ValidationError({"course_unlock_date": "Unlock date is mandatory for locked courses."})
        if unlock_date and not lp.start_date <= unlock_date.date() <= lp.end_date:
            lp_date_range = f"{lp.start_date} - {lp.end_date}"
            raise serializers.ValidationError(
                {"course_unlock_date": f"Date must be within the Learning Path's schedule range ({lp_date_range})"}
            )
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence, duration & count."""

        lp = validated_data["learning_path"]
        max_position = (
            lp.related_learning_path_courses.order_by("-sequence").values_list("sequence", flat=True).first()
        )
        validated_data["sequence"] = max_position + 1 if max_position else 1
        instance = super().create(validated_data)
        instance.learning_path.duration_course_count_update()
        return instance


class LearningPathResourceCreateModelSerializer(CommonResourceCreateModelSerializer):
    """Serializer class to upload learning path resources."""

    class Meta(CommonResourceCreateModelSerializer.Meta):
        model = LearningPathResource
        fields = CommonResourceCreateModelSerializer.Meta.fields + ["learning_path"]


class LearningPathResourceListModelSerializer(CommonResourceListModelSerializer):
    """Serializer class to list the LearningPath resources."""

    class Meta(CommonResourceListModelSerializer.Meta):
        model = LearningPathResource
