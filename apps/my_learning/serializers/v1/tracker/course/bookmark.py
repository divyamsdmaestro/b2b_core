from django.db.models import Q
from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.my_learning.models import UserCourseBookMark
from apps.my_learning.models.enrollment import Enrollment
from apps.my_learning.serializers.v1.tracker.course.sub_module import CourseSubModuleTrackerListSerializer


class UserCourseBookMarkCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to bookmark th sub_module."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserCourseBookMark
        fields = [
            "sub_module_tracker",
        ]

    def validate(self, attrs):
        """Overridden to validate the course is enrolled by a user or not."""

        sub_module_tracker = attrs["sub_module_tracker"]
        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        enrollment_instance = Enrollment.objects.filter(
            Q(user_group__in=user_groups) | Q(user=user), course=sub_module_tracker.sub_module.module.course
        ).first()
        if not enrollment_instance:
            raise serializers.ValidationError({"sub_module_tracker": "Course not enrolled."})
        attrs["user"] = user

        return attrs


class UserCourseBookMarkListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the bookmarks."""

    sub_module_tracker = CourseSubModuleTrackerListSerializer(read_only=True)

    class Meta:
        model = UserCourseBookMark
        fields = [
            "id",
            "sub_module_tracker",
        ]
