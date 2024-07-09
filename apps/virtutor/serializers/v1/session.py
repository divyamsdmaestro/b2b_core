from django.db.models import Q
from rest_framework import serializers

from apps.access_control.config import RoleTypeChoices
from apps.common.serializers import AppModelSerializer, AppSerializer
from apps.learning.models import Course
from apps.learning.validators import end_date_validation
from apps.my_learning.models import Enrollment
from apps.virtutor.config import SessionJoinMechanismChoices
from apps.virtutor.models import ScheduledSession, Trainer


class SessionScheduleSerializer(AppModelSerializer):
    """Serializer class to schedule sessions."""

    trainer = serializers.PrimaryKeyRelatedField(queryset=Trainer.objects.all())
    feedback_template_id = serializers.IntegerField(allow_null=True, required=False)
    join_mechanism = serializers.ChoiceField(choices=SessionJoinMechanismChoices.choices, required=False)

    class Meta:
        model = ScheduledSession
        fields = [
            "trainer",
            "module",
            "start_date",
            "end_date",
            "session_title",
            "recording_days",
            "creator_role",
            "feedback_template_id",
            "join_mechanism",
        ]

    def validate(self, attrs):
        """Validate the attributes."""

        end_date_validation(attrs)
        user = self.get_user()
        if not user.current_role:
            raise serializers.ValidationError({"user": "You are not allowed to perform this action."})
        if user.current_role.role_type == RoleTypeChoices.learner:
            if not user.related_enrollments.filter(is_enrolled=True, course=attrs["module"].course.id):
                raise serializers.ValidationError(
                    {"module": "You must be enrolled in this course to schedule a session"}
                )
        elif not attrs.get("join_mechanism"):
            raise serializers.ValidationError({"join_mechanism": "This field is required."})
        return attrs


class SessionManagementSerializer(AppSerializer):
    """Serializer class for the same view."""

    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive(), required=False)

    def validate(self, attrs):
        """Validate the user's role type is either admin or learner."""

        user = self.get_user()
        if not user.current_role:
            raise serializers.ValidationError({"user": "User Role is not specified."})
        if user.current_role.role_type not in [RoleTypeChoices.admin, RoleTypeChoices.learner]:
            raise serializers.ValidationError({"user": "Current User Role Type is not allowed."})
        if attrs.get("course") and user.current_role.role_type == RoleTypeChoices.learner:
            user_groups = user.related_user_groups.all().values_list("id", flat=True)
            enrollment_instance = Enrollment.objects.filter(
                Q(user_group__in=user_groups) | Q(user=user), course=attrs["course"].id
            ).first()
            if not enrollment_instance:
                raise serializers.ValidationError({"user": "Current User is not enrolled in the given course."})
        return attrs
