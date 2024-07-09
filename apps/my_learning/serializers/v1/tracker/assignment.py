from django.template import Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from apps.access.models import User
from apps.common.helpers import get_tenant_website_url
from apps.common.serializers import (
    AppCreateModelSerializer,
    AppReadOnlyModelSerializer,
    AppSerializer,
    AppUpdateModelSerializer,
    BaseIDNameSerializer,
)
from apps.common.tasks import SendEmailTask
from apps.learning.config import EvaluationTypeChoices, PlaygroundToolChoices
from apps.learning.helpers import get_ccms_retrieve_details
from apps.learning.models import Assignment
from apps.learning.models.alp.advanced_learning_path import AdvancedLearningPath
from apps.learning.models.course.course import Course
from apps.learning.models.learning_path.learning_path import LearningPath
from apps.learning.models.skill_traveller.skill_traveller import SkillTraveller
from apps.learning.serializers.v1 import AssignmentDocumentRetrieveModelSerializer, AssignmentRetrieveModelSerializer
from apps.mailcraft.config import MailTypeChoices, TemplateFieldChoices
from apps.mailcraft.models import MailTemplate
from apps.my_learning.config import AllBaseLearningTypeChoices, AssignmentLearningTypeChoices, LearningStatusChoices
from apps.my_learning.helpers import assignment_config_detail
from apps.my_learning.models import (
    AssignmentSubmission,
    AssignmentTracker,
    AssignmentYakshaResult,
    AssignmentYakshaSchedule,
    SubmissionFile,
)
from apps.my_learning.serializers.v1 import (
    BaseYakshaAssessmentResultListSerializer,
    BaseYakshaAssessmentScheduleListSerializer,
    UserBaseLearningListSerializer,
    UserBaseLearningRetrieveModelSerializer,
)
from apps.tenant_service.middlewares import get_current_db_name, get_current_sender_email


class UserAssignmentListModelSerializer(UserBaseLearningListSerializer):
    """Serializer for assignments with enrollment details."""

    author = BaseIDNameSerializer(many=True)

    class Meta(UserBaseLearningListSerializer.Meta):
        model = Assignment
        fields = UserBaseLearningListSerializer.Meta.fields + [
            "type",
            "guidance_type",
            "author",
        ]


class UserAssignmentRetrieveModelSerializer(
    AssignmentRetrieveModelSerializer, UserBaseLearningRetrieveModelSerializer
):
    """Serializer class to retrieve assignment."""

    class Meta(AssignmentRetrieveModelSerializer.Meta):
        fields = AssignmentRetrieveModelSerializer.Meta.fields + [
            "enrolled_details",
            "tracker_detail",
            "user_favourite",
            "is_feedback_given",
        ]


class UserAssignmentTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for assignment tracker details."""

    assignment = BaseIDNameSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = AssignmentTracker
        fields = [
            "id",
            "assignment",
            "ccms_id",
            "enrollment",
            "progress",
            "completed_duration",
            "allowed_attempt",
            "available_attempt",
            "last_accessed_on",
            "is_pass",
            "is_completed",
            "is_ccms_obj",
            "completion_date",
        ]


class UserAssignmentTrackerCreateModelSerializer(AppCreateModelSerializer):
    """Serializer class to start the course & add the trackers for both modules & sub_modules."""

    class Meta(AppCreateModelSerializer.Meta):
        model = AssignmentTracker
        fields = [
            "enrollment",
            "assignment",
            "ccms_id",
            "is_ccms_obj",
        ]

    def validate(self, attrs):
        """Overridden to check the enrolled course list."""

        enrollment_instance = attrs["enrollment"]
        if (
            enrollment_instance.user != self.get_user()
            and enrollment_instance.user_group not in self.get_user().related_user_groups.all()
        ):
            raise serializers.ValidationError({"enrollment": "Detail not found."})
        if not enrollment_instance.is_enrolled:
            raise serializers.ValidationError({"enrollment": "Admin approval is pending."})
        if attrs["is_ccms_obj"]:
            attrs["assignment"] = None
            if not attrs["ccms_id"]:
                raise serializers.ValidationError({"ccms_id": "This field is required."})
            if self.get_user().related_assignment_trackers.filter(ccms_id=attrs["ccms_id"]).first():
                raise serializers.ValidationError({"ccms_id": "Already started."})
        else:
            attrs["ccms_id"] = None
            if not attrs["assignment"]:
                raise serializers.ValidationError({"assignment": "This field is required."})
            if self.get_user().related_assignment_trackers.filter(assignment=attrs["assignment"]).first():
                raise serializers.ValidationError({"enrollment": "Already started."})
        return attrs

    def create(self, validated_data):
        """Create a tracker for course."""

        assignment = validated_data["assignment"]
        if validated_data["is_ccms_obj"]:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment",
                instance_id=validated_data["ccms_id"],
                request={"headers": dict(self.context["request"].headers)},
            )
            assignment_id = None
            if success:
                assignment_tool = data["data"]["tool"]
                allowed_attempts = data["data"]["allowed_attempts"]
            else:
                raise serializers.ValidationError({"ccms_id": data["data"]})
        else:
            assignment_tool = assignment.tool
            assignment_id = assignment.id
            allowed_attempts = assignment.allowed_attempts
        assignment_config = assignment_config_detail(
            assignment_id=assignment_id, enrollment=validated_data["enrollment"], choice=assignment_tool
        )
        if not assignment_config:
            raise serializers.ValidationError({"enrollment": "Configuration not found. Contact administrator."})
        validated_data["user"] = self.get_user()
        instance = super().create(validated_data)
        instance.allowed_attempt = instance.available_attempt = allowed_attempts or assignment_config.allowed_attempts
        instance.save()
        instance.enrollment.learning_status = LearningStatusChoices.started
        instance.enrollment.save()
        return instance


class UserAssignmentStartSerializer(AppSerializer):
    """Serializer class for start the assignment."""

    tracker = serializers.PrimaryKeyRelatedField(queryset=AssignmentTracker.objects.all(), required=True)
    learning_type = serializers.ChoiceField(choices=AssignmentLearningTypeChoices.choices, required=True)
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
    ccms_id = serializers.CharField(allow_null=True, required=False)
    is_ccms_obj = serializers.BooleanField(required=False)

    def validate(self, attrs):
        """Overridden to validate the necessary fields."""

        learning_type = attrs.get("learning_type")
        tracker = attrs.get("tracker")
        if tracker.user != self.get_user():
            raise serializers.ValidationError({"tracker": "Detail not found."})
        if attrs.get("is_ccms_obj"):
            ccms_id = attrs.get("ccms_id")
            if not ccms_id:
                raise serializers.ValidationError({"ccms_id": "This field is required"})
            success, data = get_ccms_retrieve_details(
                learning_type="assignment",
                instance_id=ccms_id,
                request={"headers": dict(self.context["request"].headers)},
            )
            if success:
                assignment_tool = data["data"]["tool"]
                mml_sku_id = data["data"]["mml_sku_id"]
            else:
                raise serializers.ValidationError({"ccms_id": data["data"]})
        else:
            learning_instance = attrs.get(learning_type)
            if not learning_instance:
                raise serializers.ValidationError({learning_type: "This field is required"})
            assignment_tool = tracker.assignment.tool
            mml_sku_id = getattr(learning_instance, "mml_sku_id", None)
        if assignment_tool == PlaygroundToolChoices.mml and mml_sku_id is None:
            raise serializers.ValidationError({learning_type: "Lab not found."})
        return attrs


class SubmissionFileRetrieveSerializer(AppReadOnlyModelSerializer):
    """Serializer class for retrieving submission files."""

    class Meta:
        model = SubmissionFile
        fields = ["id", "file"]


class AssignmentSubmissionCreateModelSerializer(AppCreateModelSerializer):
    """Serializer class for submitting the assignments."""

    pass_percentage = serializers.IntegerField(required=False)

    class Meta(AppCreateModelSerializer.Meta):
        model = AssignmentSubmission
        fields = [
            "assignment_tracker",
            "files",
            "description",
            "pass_percentage",
        ]

    def validate(self, attrs):
        """Validate the no of files allowed per submission & tracker submission."""

        files = attrs["files"]
        assignment_tracker = attrs["assignment_tracker"]
        if assignment_tracker.user != self.get_user():
            raise serializers.ValidationError({"assignment_tracker": "Invalid tracker."})
        if assignment_tracker.available_attempt == 0:
            raise serializers.ValidationError({"assignment_tracker": "Max attempts reached."})
        # TODO: This is temporary solution need to provide support for if the assignment was started.
        if not assignment_tracker.allowed_attempt:
            raise serializers.ValidationError("Assignment not started.")
        if assignment_tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment",
                instance_id=assignment_tracker.ccms_id,
                request={"headers": dict(self.context["request"].headers)},
            )
            if success:
                assignment_name = data["data"]["name"]
                assignment_id = data["data"]["id"]
                assignment_tool = data["data"]["tool"]
                enable_submission = data["data"]["enable_submission"]
                evaluation_type = data["data"]["evaluation_type"]
            else:
                raise serializers.ValidationError({"ccms_id": data["data"]})
        else:
            assignment_name = assignment_tracker.assignment.name
            assignment_id = assignment_tracker.assignment.id
            assignment_tool = assignment_tracker.assignment.tool
            enable_submission = assignment_tracker.assignment.enable_submission
            evaluation_type = assignment_tracker.assignment.evaluation_type
        if assignment_tool == PlaygroundToolChoices.yaksha or not enable_submission:
            raise serializers.ValidationError("Submission not allowed.")
        submission_config = assignment_config_detail(
            assignment_id=assignment_id,
            enrollment=assignment_tracker.enrollment,
            choice=assignment_tool,
        )
        if not submission_config:
            return serializers.ValidationError(
                {"assignment_tracker": "Configuration not found. Contact administrator."}
            )
        if len(files) > submission_config.max_files_allowed:
            raise serializers.ValidationError(
                {"files": f"Max allowed files per submission is {submission_config.max_files_allowed}"}
            )
        attrs["pass_percentage"] = submission_config.pass_percentage
        attrs["evaluation_type"] = evaluation_type
        attrs["assignment_name"] = assignment_name
        return attrs

    def send_file_submission_email(self, assignment_name, db_name, instance):
        """function to call Report EmailTask"""

        mail_template = MailTemplate.objects.all().filter(type=MailTypeChoices.user_assignment_upload).first()
        if mail_template:
            recipients = []
            if not instance.assignment_tracker.is_ccms_obj:
                recipients = list(instance.assignment_tracker.assignment.author.all().values_list("email", flat=True))
            if not recipients:
                recipients = [User.objects.filter(is_staff=True).first().email]
            url = get_tenant_website_url(db_name)
            email_context = {
                TemplateFieldChoices.user_name: instance.assignment_tracker.user.name,
                TemplateFieldChoices.artifact_name: assignment_name,
                TemplateFieldChoices.completion_date: instance.created_at,
                TemplateFieldChoices.website_url: url,
            }
            sender_email = get_current_sender_email()
            template = Template(mail_template.content)
            html_body = template.render(Context(email_context))
            files_list = list(instance.files.values_list("file", flat=True))
            SendEmailTask().run_task(
                subject=mail_template.subject,
                message=strip_tags(html_body),
                recipients=recipients,
                sender_email=sender_email,
                html_message=html_body,
                attachments=files_list,
                is_default_storage=True,
            )
        return True

    def create(self, validated_data):
        """Overridden to update the attempt."""

        tracker = validated_data["assignment_tracker"]
        assignment_name = validated_data.pop("assignment_name")
        evaluation_type = validated_data.pop("evaluation_type")
        attempt = len(tracker.related_assignment_submissions.all()) + 1
        if attempt > tracker.allowed_attempt:
            raise serializers.ValidationError({"assignment_tracker": "Max attempts reached."})
        validated_data["attempt"] = attempt
        instance = super().create(validated_data)
        if evaluation_type == EvaluationTypeChoices.non_evaluated:
            tracker.is_completed = True
            tracker.is_pass = True
            tracker.completion_date = timezone.now()
            tracker.last_accessed_on = timezone.now()
            tracker.progress = 100
            instance.is_pass = True
            instance.save()
            tracker.save()
            if not tracker.is_ccms_obj:
                self.get_user().related_skill_ontology_progress_update(
                    AllBaseLearningTypeChoices.assignment, tracker.assignment
                )
                tracker.assignment_relation_progress_update()
        tracker.available_attempt = tracker.available_attempt - 1 if tracker.available_attempt != 0 or None else 0
        tracker.save()
        self.send_file_submission_email(assignment_name, get_current_db_name(), instance)
        return instance


class AssignmentSubmissionListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for listing assignments."""

    class AssignmentSerializer(BaseIDNameSerializer):
        """Serializer class to retrieve Assignment file"""

        file = AssignmentDocumentRetrieveModelSerializer(read_only=True)

    files = SubmissionFileRetrieveSerializer(many=True, read_only=True)
    evaluator = BaseIDNameSerializer(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    user_group = serializers.SerializerMethodField(read_only=True)
    assignment = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        """Returns the assignment name for the given assignment submission."""

        return BaseIDNameSerializer(obj.assignment_tracker.user).data

    def get_user_group(self, obj):
        """Returns the user group details associated with the user object."""

        if user_group := obj.assignment_tracker.user.related_user_groups.first():
            return BaseIDNameSerializer(user_group).data
        return None

    def get_assignment(self, obj):
        """Returns the assignment name for the given assignment submission."""

        if obj.assignment_tracker.is_ccms_obj:
            if assignment_data := self.context.get("assignment"):
                return assignment_data
            return {"id": obj.assignment_tracker.ccms_id, "is_ccms_obj": True}
        else:
            return self.AssignmentSerializer(obj.assignment_tracker.assignment).data

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "user",
            "user_group",
            "assignment_tracker",
            "files",
            "description",
            "pass_percentage",
            "progress",
            "evaluator",
            "feedback",
            "is_pass",
            "is_reviewed",
        ]


class AssignmentSubmissionUpdateModelSerializer(AppUpdateModelSerializer):
    """Serializer class for update the assignment submission."""

    class Meta(AppUpdateModelSerializer.Meta):
        model = AssignmentSubmission
        fields = [
            "feedback",
            "progress",
        ]

    def update(self, instance, validated_data):
        """Overridden to update the status."""

        user = self.get_user()
        instance = super().update(instance, validated_data)
        instance.is_pass = True if instance.progress >= instance.pass_percentage else False
        instance.evaluator = user
        instance.is_reviewed = True
        instance.save()
        assignment_tracker = instance.assignment_tracker
        if assignment_tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment",
                instance_id=assignment_tracker.ccms_id,
                request={"headers": dict(self.context["request"].headers)},
            )
            if success:
                evaluation_type = data["data"]["evaluation_type"]
            else:
                raise serializers.ValidationError({"ccms_id": data["data"]})
        else:
            evaluation_type = assignment_tracker.assignment.evaluation_type
        if evaluation_type == EvaluationTypeChoices.evaluated:
            if instance.progress >= instance.pass_percentage:
                assignment_tracker.progress, assignment_tracker.is_pass = 100, True
        else:
            assignment_tracker.progress, assignment_tracker.is_pass = 100, True
        assignment_tracker.is_completed = True
        assignment_tracker.completion_date = timezone.now()
        assignment_tracker.save()
        if not assignment_tracker.is_ccms_obj:
            user.related_skill_ontology_progress_update(
                AllBaseLearningTypeChoices.assignment, assignment_tracker.assignment
            )
            assignment_tracker.assignment_relation_progress_update()
        return instance


class AssignmentYakshaScheduleListSerializer(BaseYakshaAssessmentScheduleListSerializer):
    """Serializer for AssignmentYakshaScheduleList."""

    class Meta(BaseYakshaAssessmentScheduleListSerializer.Meta):
        model = AssignmentYakshaSchedule
        fields = BaseYakshaAssessmentScheduleListSerializer.Meta.fields + ["assignment_tracker"]


class AssignmentYakshaResultListSerializer(BaseYakshaAssessmentResultListSerializer):
    """Serializer class for assignment yaksha result."""

    class Meta(BaseYakshaAssessmentResultListSerializer.Meta):
        model = AssignmentYakshaResult
        fields = BaseYakshaAssessmentResultListSerializer.Meta.fields + ["schedule"]
