from django.utils import timezone
from rest_framework import serializers

from apps.access.models.user import User
from apps.access_control.models import UserGroup
from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer, AppSerializer
from apps.learning.config import BaseUploadStatusChoices
from apps.learning.models import (
    AdvancedLearningPath,
    Assignment,
    AssignmentGroup,
    Course,
    LearningPath,
    SkillTraveller,
)
from apps.learning.validators import end_date_validation
from apps.my_learning.models import Report
from apps.my_learning.tasks import (
    FeedbackReportGenerationTask,
    FileSubmissionReportGenerationTask,
    ReportGenerationTask,
)
from apps.tenant_service.middlewares import get_current_db_name


class ReportEmailCreateSerializer(AppSerializer):
    """Serializer to handle Email Report"""

    is_send_email = serializers.BooleanField(default=False)
    recipients = serializers.PrimaryKeyRelatedField(queryset=User.objects.active(), many=True, required=False)

    def validate(self, attrs):
        """Function to validate recipients"""

        if attrs.get("is_send_email") and not attrs.get("recipients"):
            raise serializers.ValidationError({"recipients": "This field is required"})
        return attrs


class ReportCreateSerializer(AppCreateModelSerializer, ReportEmailCreateSerializer):
    """Create serializer for `Report` model."""

    is_entire_learnings = serializers.BooleanField()
    is_file_submission = serializers.BooleanField(required=False)
    is_feedback_report = serializers.BooleanField(required=False)
    is_evaluated = serializers.BooleanField(required=False)
    is_date_skipped = serializers.BooleanField()
    is_master_report = serializers.BooleanField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.unarchived(), many=True)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.unarchived(), many=True)
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.unarchived(), many=True
    )
    skill_traveller = serializers.PrimaryKeyRelatedField(queryset=SkillTraveller.objects.unarchived(), many=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.unarchived(), many=True)
    assignment_group = serializers.PrimaryKeyRelatedField(queryset=AssignmentGroup.objects.unarchived(), many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.active(), many=True)
    user_group = serializers.PrimaryKeyRelatedField(queryset=UserGroup.objects.alive(), many=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = Report
        fields = [
            "name",
            "user",
            "user_group",
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
            "assignment",
            "assignment_group",
            "start_date",
            "end_date",
            "is_entire_learnings",
            "is_date_skipped",
            "is_master_report",
            "is_file_submission",
            "is_evaluated",
            "is_feedback_report",
            "is_send_email",
            "recipients",
        ]

    def validate(self, attrs):
        """Overriden to validate the attributes"""

        attrs = super().validate(attrs)
        if not attrs["is_date_skipped"]:
            if not attrs.get("start_date"):
                raise serializers.ValidationError({"start_date": "This field is required"})
            if not attrs.get("end_date"):
                raise serializers.ValidationError({"end_date": "This field is required"})
            end_date_validation(attrs)
            current_date = timezone.now().date()
            if attrs["end_date"] > current_date:
                raise serializers.ValidationError({"end_date": "Date should be less than current date."})
            if (attrs["end_date"] - attrs["start_date"]).days > 366:
                raise serializers.ValidationError({"start_date": "Date range should not exceed one year."})
        if not attrs["is_entire_learnings"] and not (
            attrs["course"]
            or attrs["learning_path"]
            or attrs["advanced_learning_path"]
            or attrs["skill_traveller"]
            or attrs["assignment"]
            or attrs["assignment_group"]
        ):
            raise serializers.ValidationError({"course": "Select any learnings for this report."})
        if attrs.get("is_file_submission") and attrs.get("is_evaluated") is None:
            raise serializers.ValidationError({"is_evaluated": "This field is required."})
        attrs["is_file_submission"] = attrs.get("is_file_submission", False)
        attrs["is_evaluated"] = attrs.get("is_evaluated", False)
        attrs["is_feedback_report"] = attrs.get("is_feedback_report", False)
        return attrs

    def create(self, validated_data):
        """Overriden to call the report generation task."""

        data = self.get_request().data
        is_file_submission = validated_data.pop("is_file_submission")
        is_feedback_report = validated_data.pop("is_feedback_report")
        is_send_email = validated_data.pop("is_send_email")
        # Note: Any changes in keys modify the same in TechademyOne Report API.
        validated_data["data"] = {
            "is_entire_learnings": validated_data.pop("is_entire_learnings"),
            "is_date_skipped": validated_data.pop("is_date_skipped"),
            "is_master_report": validated_data.pop("is_master_report"),
            "is_file_submission": is_file_submission,
            "is_evaluated": validated_data.pop("is_evaluated"),
            "is_feedback_report": is_feedback_report,
            "course": data.get("course"),
            "course_name": [course.name for course in validated_data.pop("course")],
            "learning_path": data.get("learning_path"),
            "learning_path_name": [lp.name for lp in validated_data.pop("learning_path")],
            "advanced_learning_path": data.get("advanced_learning_path"),
            "advanced_learning_path_name": [alp.name for alp in validated_data.pop("advanced_learning_path")],
            "skill_traveller": data.get("skill_traveller"),
            "skill_traveller_name": [st.name for st in validated_data.pop("skill_traveller")],
            "assignment": data.get("assignment"),
            "assignment_name": [assignment.name for assignment in validated_data.pop("assignment")],
            "assignment_group": data.get("assignment_group"),
            "assignment_group_name": [ag.name for ag in validated_data.pop("assignment_group")],
            "user": data.get("user"),
            "user_name": [user.username for user in validated_data.pop("user")],
            "user_group": data.get("user_group"),
            "user_group_name": [user_group.name for user_group in validated_data.pop("user_group")],
            "is_send_email": is_send_email,
            "recipients": [recipient.email for recipient in validated_data.pop("recipients", [])],
        }
        instance = super().create(validated_data)
        instance.status = BaseUploadStatusChoices.initiated
        instance.save()
        if is_file_submission:
            FileSubmissionReportGenerationTask().run_task(
                report_instance_id=instance.id,
                db_name=get_current_db_name(),
            )
        elif is_feedback_report:
            FeedbackReportGenerationTask().run_task(report_instance_id=instance.id, db_name=get_current_db_name())
        else:
            ReportGenerationTask().run_task(
                report_instance_id=instance.id,
                db_name=get_current_db_name(),
                request_headers={"headers": dict(self.get_request().headers)},
            )
        return instance


class ReportListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `Report` model."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = ["id", "name", "start_date", "end_date", "status"]
        model = Report
