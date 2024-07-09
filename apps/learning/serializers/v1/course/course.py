from rest_framework import serializers

from apps.common.helpers import process_request_headers
from apps.forum.models import Forum, ForumCourseRelationModel
from apps.learning.models import Course, CourseResource
from apps.learning.serializers.v1.common import (
    BaseLearningListModelSerializer,
    BaseLearningSkillRoleCUDModelSerializer,
    BaseLearningSkillRoleRetrieveModelSerializer,
    CommonResourceCreateModelSerializer,
    CommonResourceListModelSerializer,
)
from apps.learning.validators import draft_action
from apps.meta.models import Faculty
from apps.meta.serializers.v1.faculty import FacultyListModelSerializer


class CourseCUDModelSerializer(BaseLearningSkillRoleCUDModelSerializer):
    """Course creation model serializer."""

    rating = serializers.FloatField(required=False)
    forums = serializers.PrimaryKeyRelatedField(queryset=Forum.objects.alive(), many=True, required=False)

    class Meta(BaseLearningSkillRoleCUDModelSerializer.Meta):
        """Metaclass contains all fields in the model."""

        model = Course
        fields = BaseLearningSkillRoleCUDModelSerializer.Meta.fields + [
            "catalogue",
            "author",
            "mml_sku_id",
            "vm_name",
        ]

    def create(self, validated_data):
        """Overridden to change the active field when the data to be save as draft."""

        validated_data = draft_action(validated_data)
        validated_data["duration"] = 0
        forums = validated_data.pop("forums")
        instance: Course = super().create(validated_data=validated_data)
        instance.role.all().role_course_count_update()
        instance.skill.all().skill_course_count_update()
        instance.category.category_course_count_update()
        if forums:
            ForumCourseRelationModel.objects.bulk_create(
                ForumCourseRelationModel(course=instance, forum=forum) for forum in forums
            )
        request_headers = process_request_headers(request={"headers": dict(self.context["request"].headers)})
        instance.register_course_in_chat_service(request_headers=request_headers)
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the skill, role& category course count & the draft field to instance."""

        forums = validated_data.pop("forums")
        instance = super().update(instance=instance, validated_data=validated_data)
        instance.role.all().role_course_count_update()
        instance.skill.all().skill_course_count_update()
        instance.category.category_course_count_update()
        if forums:
            instance.related_forum_course_relations.exclude(forum__in=forums).delete()
            for forum in forums:
                ForumCourseRelationModel.objects.update_or_create(course=instance, forum=forum)
        else:
            instance.related_forum_course_relations.all().delete()
        return instance

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["forums"] = Forum.objects.filter(related_forum_course_relations__course=self.instance).values_list(
            "id", flat=True
        )
        return meta

    def get_meta(self) -> dict:
        """Get meta & initial values for courses."""

        meta = super().get_meta()
        meta.update(
            {
                "author": self.serialize_for_meta(Faculty.objects.all(), fields=["id", "name"]),
            }
        )
        return meta


class CourseListModelSerializer(BaseLearningListModelSerializer):
    """Serializer class for course list."""

    class Meta(BaseLearningListModelSerializer.Meta):
        model = Course
        fields = BaseLearningListModelSerializer.Meta.fields


class CourseRetrieveModelSerializer(BaseLearningSkillRoleRetrieveModelSerializer):
    """Retrieve serializer for course."""

    author = FacultyListModelSerializer(read_only=True)
    forums = serializers.ListField(source="forum_as_id", read_only=True)

    class Meta(BaseLearningSkillRoleRetrieveModelSerializer.Meta):
        model = Course
        fields = BaseLearningSkillRoleRetrieveModelSerializer.Meta.fields + [
            "author",
            "vm_name",
            "mml_sku_id",
            "total_modules",
            "total_sub_modules",
        ]


class CourseResourceCreateModelSerializer(CommonResourceCreateModelSerializer):
    """Serializer class to upload course resources."""

    class Meta(CommonResourceCreateModelSerializer.Meta):
        model = CourseResource
        fields = CommonResourceCreateModelSerializer.Meta.fields + ["course"]


class CourseResourceListModelSerializer(CommonResourceListModelSerializer):
    """Serializer class to list the course resources."""

    class Meta(CommonResourceListModelSerializer.Meta):
        model = CourseResource
