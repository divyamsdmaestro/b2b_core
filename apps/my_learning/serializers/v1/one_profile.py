from rest_framework import serializers

from apps.access.models import UserDetail, UserEducationDetail
from apps.common.serializers import AppReadOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.models import Course
from apps.my_learning.config import EnrollmentTypeChoices
from apps.my_learning.models import CourseAssessmentTracker, LPAssessmentTracker, UserCourseTracker
from apps.my_learning.serializers.v1 import CAYakshaResultListSerializer, LPAYakshaResultListSerializer


class UserEducationDetailSerializer(AppReadOnlyModelSerializer):
    """Serializer to retrieve user education details."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserEducationDetail
        fields = ["id", "name", "education_type", "university", "degree"]


class OneProfileUserInfoSerializer(AppReadOnlyModelSerializer):
    """Serializer to retrieve one profile user informations."""

    job_title = BaseIDNameSerializer(read_only=True)
    education_detail = UserEducationDetailSerializer(many=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserDetail
        fields = [
            "job_title",
            "contact_number",
            "education_detail",
        ]


class CourseSerializer(AppReadOnlyModelSerializer):
    """Serializer to retrieve course details."""

    skill = BaseIDNameSerializer(many=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Course
        fields = ["id", "name", "skill", "certificate", "mml_sku_id", "vm_name"]


class OneProfileCourseInfoSerializer(AppReadOnlyModelSerializer):
    """Serializer to retrieve one profile course informations."""

    course = CourseSerializer(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        """Returns the learning type of the enrollment instance."""

        return EnrollmentTypeChoices.get_choice(obj.enrollment.learning_type).label

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserCourseTracker
        fields = ["course", "completion_date", "progress", "completed_duration", "type"]


class OneProfileCourseAssessmentSerializer(CAYakshaResultListSerializer):
    """Serializer to retrieve one profile course assessment informations."""

    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        """Returns the course assessment name"""

        return CourseAssessmentTracker.objects.filter(related_ca_yaksha_schedules=obj.schedule).first().assessment.name

    class Meta(CAYakshaResultListSerializer.Meta):
        fields = CAYakshaResultListSerializer.Meta.fields + ["name"]


class OneProfileLPAssessmentSerializer(LPAYakshaResultListSerializer):
    """Serializer to retrieve one profile lp assessment informations."""

    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        """Returns the lp assessment name"""

        return LPAssessmentTracker.objects.filter(related_lpa_yaksha_schedules=obj.schedule).first().assessment.name

    class Meta(LPAYakshaResultListSerializer.Meta):
        fields = LPAYakshaResultListSerializer.Meta.fields + ["name"]
