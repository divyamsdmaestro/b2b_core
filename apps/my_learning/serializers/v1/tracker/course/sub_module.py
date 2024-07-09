from django.template import Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from apps.access.models.user import User
from apps.common.helpers import get_tenant_website_url
from apps.common.serializers import (
    AppCreateModelSerializer,
    AppReadOnlyModelSerializer,
    AppUpdateModelSerializer,
    BaseIDNameSerializer,
)
from apps.common.tasks.outbound import SendEmailTask
from apps.learning.config import EvaluationTypeChoices, SubModuleTypeChoices
from apps.learning.helpers import get_ccms_retrieve_details
from apps.learning.serializers.v1 import CourseSubModuleListSerializer
from apps.mailcraft.config import MailTypeChoices, TemplateFieldChoices
from apps.mailcraft.models import MailTemplate
from apps.meta.models import MMLConfiguration
from apps.my_learning.models import CourseSubModuleTracker, SubModuleFileSubmission
from apps.my_learning.serializers.v1.tracker.assignment import SubmissionFileRetrieveSerializer
from apps.my_learning.tasks import CourseProgressUpdateTask
from apps.tenant_service.middlewares import get_current_db_name, get_current_sender_email


class CourseSubModuleTrackerListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to return the sub_module trackers."""

    user_bookmark = serializers.SerializerMethodField()

    def get_user_bookmark(self, obj):
        """Returns the sub module is bookmarked or not."""

        user_bookmark = obj.related_user_course_bookmarks.filter(user=self.get_user()).first()
        return {"id": user_bookmark.id if user_bookmark else None, "is_bookmarked": bool(user_bookmark)}

    class Meta:
        model = CourseSubModuleTracker
        fields = [
            "id",
            "sub_module",
            "module_tracker",
            "ccms_id",
            "progress",
            "completed_duration",
            "created_at",
            "created_by",
            "user_bookmark",
            "is_completed",
            "completion_date",
            "is_ccms_obj",
        ]


class UserCourseSubModuleListSerializer(CourseSubModuleListSerializer):
    """Submodule list serializer class with tracker details."""

    tracker_details = serializers.SerializerMethodField()

    def get_tracker_details(self, obj):
        """Returns the tracker details of submodule."""

        instance = obj.related_course_sub_module_trackers.filter(
            module_tracker__course_tracker__user=self.get_user()
        ).first()
        return CourseSubModuleTrackerListSerializer(instance, context=self.context).data if instance else None

    class Meta(CourseSubModuleListSerializer.Meta):
        fields = CourseSubModuleListSerializer.Meta.fields + [
            "tracker_details",
        ]


class CourseSubModuleTrackerCreateSerializer(AppCreateModelSerializer):
    """Serializer class to create a course module tracker."""

    class Meta(AppCreateModelSerializer.Meta):
        model = CourseSubModuleTracker
        fields = [
            "module_tracker",
            "sub_module",
            "ccms_id",
            "is_ccms_obj",
        ]

    def validate(self, attrs):
        """Validate the course tracker & module is valid or not."""

        module_tracker = attrs.get("module_tracker")
        sub_module = attrs.get("sub_module")
        if module_tracker.course_tracker.user != self.get_user():
            raise serializers.ValidationError({"module_tracker": "Invalid tracker details provided."})
        if attrs["is_ccms_obj"]:
            attrs["sub_module"] = None
            if not attrs["ccms_id"]:
                raise serializers.ValidationError({"ccms_id": "This field is required."})
            if module_tracker.related_course_sub_module_trackers.filter(ccms_id=attrs["ccms_id"]).first():
                raise serializers.ValidationError({"ccms_id": "Already started."})
        else:
            attrs["ccms_id"] = None
            if not sub_module:
                raise serializers.ValidationError({"sub_module": "This field is required."})
            if sub_module not in module_tracker.module.related_course_sub_modules.all():
                raise serializers.ValidationError({"module_tracker": "Invalid sub module details provided."})
            if module_tracker.related_course_sub_module_trackers.filter(sub_module=sub_module).first():
                raise serializers.ValidationError({"sub_module": "Already started."})
        return attrs


class CourseSubModuleTrackerUpdateSerializer(AppUpdateModelSerializer):
    """Serializer class to update the sub_module tracker."""

    class Meta(AppUpdateModelSerializer.Meta):
        model = CourseSubModuleTracker
        fields = ["completed_duration"]

    def update(self, instance, validated_data):
        """Update the sub_module tracker."""

        if instance.module_tracker.course_tracker.user != self.get_user():
            raise serializers.ValidationError({"id": "Detail not found."})
        if not instance.is_ccms_obj:
            duration = instance.sub_module.duration
            if duration and validated_data["completed_duration"] > duration:
                raise serializers.ValidationError(
                    {"completed_duration": "Duration not more than the actual duration."}
                )
        instance = super().update(instance, validated_data)
        request = {"headers": dict(self.context["request"].headers)}
        CourseProgressUpdateTask().run_task(db_name=get_current_db_name(), tracker=instance.id, request=request)
        return instance


class CourseSubModuleTrackerRetrieveSerializer(AppReadOnlyModelSerializer):
    """Serializer class to return the sub_module trackers."""

    sub_module = CourseSubModuleListSerializer(read_only=True)
    user_bookmark = serializers.SerializerMethodField()

    def get_user_bookmark(self, obj):
        """Returns the sub module is bookmarked or not."""

        user_bookmark = obj.related_user_course_bookmarks.filter(user=self.get_user()).first()
        return {"id": user_bookmark.id if user_bookmark else None, "is_bookmarked": bool(user_bookmark)}

    class Meta:
        model = CourseSubModuleTracker
        fields = [
            "id",
            "sub_module",
            "module_tracker",
            "ccms_id",
            "progress",
            "completed_duration",
            "created_at",
            "created_by",
            "user_bookmark",
            "is_completed",
            "completion_date",
            "is_ccms_obj",
        ]

    def to_representation(self, instance):
        """Overridden to return the ccms detail if it was a ccms obj."""

        results = super().to_representation(instance)
        if instance.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="course_submodule",
                instance_id=str(instance.ccms_id),
                request={"headers": dict(self.context["request"].headers)},
            )
            if success:
                results["ccms_id"] = data["data"]
                return results
            raise serializers.ValidationError(data["data"])
        return results


class SubModuleFileSubmissionCreateSerializer(AppCreateModelSerializer):
    """Serializer class for submitting the submodule files."""

    pass_percentage = serializers.IntegerField(required=False)

    class Meta(AppCreateModelSerializer.Meta):
        model = SubModuleFileSubmission
        fields = [
            "sub_module_tracker",
            "files",
            "description",
            "pass_percentage",
        ]

    def validate(self, attrs):
        """Overridden to validate the no of files allowed per submission & max attempts."""

        files = attrs["files"]
        sub_module_tracker = attrs["sub_module_tracker"]
        if sub_module_tracker.module_tracker.course_tracker.user != self.get_user():
            raise serializers.ValidationError({"sub_module_tracker": "Invalid tracker"})
        if sub_module_tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                request={"headers": dict(self.context["request"].headers)},
                learning_type="course_submodule",
                instance_id=str(sub_module_tracker.ccms_id),
            )
            if success:
                sub_module_name = data["data"]["name"]
                submodule_type = data["data"]["type"]["id"]
                evaluation_type = data["data"]["evaluation_type"]
                course = None
            else:
                raise serializers.ValidationError({"ccms_id": data["data"]})
        else:
            sub_module_name = sub_module_tracker.sub_module.name
            submodule_type = sub_module_tracker.sub_module.type
            course = sub_module_tracker.sub_module.module.course
            evaluation_type = sub_module_tracker.sub_module.evaluation_type
        if submodule_type != SubModuleTypeChoices.file_submission:
            raise serializers.ValidationError(
                {"sub_module_tracker": f"file submission is not allowed for {submodule_type}"}
            )
        submission_config = (
            MMLConfiguration.objects.filter(course=course, course__isnull=False)
            or MMLConfiguration.objects.filter(is_default=True)
        ).first()
        if not submission_config:
            return serializers.ValidationError(
                {"sub_module_tracker": "Configuration not found. Contact administrator."}
            )
        if len(files) > submission_config.max_files_allowed:
            raise serializers.ValidationError(
                {"files": f"Max allowed files per submission is {submission_config.max_files_allowed}"}
            )
        if sub_module_tracker.available_attempt <= 0:
            raise serializers.ValidationError({"sub_module_tracker": "Max attempts reached"})
        attrs["pass_percentage"] = submission_config.pass_percentage
        attrs["evaluation_type"] = evaluation_type
        attrs["sub_module_name"] = sub_module_name
        return attrs

    def send_file_submission_email(self, sub_module_name, db_name, instance):
        """function to call Report EmailTask"""

        mail_template = MailTemplate.objects.active().filter(type=MailTypeChoices.user_assignment_upload).first()
        if mail_template:
            recipients = []
            if not instance.sub_module_tracker.is_ccms_obj:
                recipients = list(instance.sub_module_tracker.sub_module.author.all().values_list("email", flat=True))
            if not recipients:
                recipients = [User.objects.filter(is_staff=True).first().email]
            url = get_tenant_website_url(db_name)
            email_context = {
                TemplateFieldChoices.user_name: instance.sub_module_tracker.module_tracker.course_tracker.user.name,
                TemplateFieldChoices.artifact_name: sub_module_name,
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

        db_name = get_current_db_name()
        tracker = validated_data["sub_module_tracker"]
        evaluation_type = validated_data.pop("evaluation_type")
        sub_module_name = validated_data.pop("sub_module_name")
        validated_data["attempt"] = len(tracker.related_sub_module_submissions.all()) + 1
        instance = super().create(validated_data)
        if evaluation_type == EvaluationTypeChoices.non_evaluated:
            tracker.is_completed = True
            tracker.completion_date = timezone.now()
            tracker.last_accessed_on = timezone.now()
            tracker.save()
            instance.is_pass = True
            instance.save()
            request = {"headers": dict(self.context["request"].headers)}
            CourseProgressUpdateTask().run_task(db_name=db_name, tracker=tracker.id, request=request)
        tracker.available_attempt -= 1
        tracker.save()
        self.send_file_submission_email(sub_module_name, db_name, instance)
        return instance


class SubModuleFileSubmissionListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for listing sub module file submissions."""

    class SubmoduleSerializer(BaseIDNameSerializer):
        """Serializer class to List sub-module file"""

        file_url = serializers.URLField()
        custom_url = serializers.CharField()

    files = SubmissionFileRetrieveSerializer(many=True, read_only=True)
    evaluator = BaseIDNameSerializer(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    user_group = serializers.SerializerMethodField(read_only=True)
    sub_module = serializers.SerializerMethodField(read_only=True)
    available_attempts = serializers.SerializerMethodField(read_only=True)
    course = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        """Returns the sub module name for the given submission."""

        return BaseIDNameSerializer(obj.sub_module_tracker.module_tracker.course_tracker.user).data

    def get_user_group(self, obj):
        """Returns the user group details associated with the user object."""

        if user_group := obj.sub_module_tracker.module_tracker.course_tracker.user.related_user_groups.first():
            return BaseIDNameSerializer(user_group).data
        return None

    def get_sub_module(self, obj):
        """Returns the sub module name for the given submission."""

        return (
            self.SubmoduleSerializer(obj.sub_module_tracker.sub_module).data
            if not obj.sub_module_tracker.is_ccms_obj
            else {
                "id": obj.sub_module_tracker.ccms_id,
                "is_ccms_obj": True,
            }
        )

    def get_available_attempts(self, obj):
        """Returns the no of attempts available for the given file submission."""

        if not obj.sub_module_tracker.is_ccms_obj:
            course = obj.sub_module_tracker.sub_module.module.course
        else:
            course = None
        submission_config = (
            MMLConfiguration.objects.filter(course=course, course__isnull=False)
            or MMLConfiguration.objects.filter(is_default=True)
        ).first()
        if not submission_config:
            return 0
        availabe_attempts = submission_config.allowed_attempts - len(
            obj.sub_module_tracker.related_sub_module_submissions.all()
        )
        return availabe_attempts if availabe_attempts > 0 else 0

    def get_course(self, obj):
        """Returns the course name."""

        return (
            obj.sub_module_tracker.sub_module.module.course.name
            if not obj.sub_module_tracker.is_ccms_obj
            else "CCMS Course"
        )

    class Meta:
        model = SubModuleFileSubmission
        fields = [
            "id",
            "course",
            "sub_module",
            "user",
            "user_group",
            "sub_module_tracker",
            "files",
            "description",
            "pass_percentage",
            "progress",
            "evaluator",
            "feedback",
            "is_pass",
            "is_reviewed",
            "created_at",
            "available_attempts",
        ]


class SubModuleFileSubmissionUpdateSerializer(AppUpdateModelSerializer):
    """Serializer class for update the sub module file submission."""

    class Meta(AppUpdateModelSerializer.Meta):
        model = SubModuleFileSubmission
        fields = [
            "feedback",
            "progress",
        ]

    def update(self, instance, validated_data):
        """Overridden to update the status."""

        instance = super().update(instance, validated_data)
        instance.is_pass = True if instance.progress >= instance.pass_percentage else False
        instance.evaluator = self.get_user()
        instance.is_reviewed = True
        instance.save()
        sub_module_tracker = instance.sub_module_tracker
        if sub_module_tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                request={"headers": dict(self.context["request"].headers)},
                learning_type="course_submodule",
                instance_id=str(sub_module_tracker.ccms_id),
            )
            if success:
                evaluation_type = data["data"]["evaluation_type"]
            else:
                raise serializers.ValidationError({"ccms_id": data["data"]})
        else:
            evaluation_type = sub_module_tracker.sub_module.evaluation_type
        if evaluation_type == EvaluationTypeChoices.evaluated:
            if instance.progress >= instance.pass_percentage:
                sub_module_tracker.progress = 100
            sub_module_tracker.is_completed = True
            sub_module_tracker.completion_date = timezone.now()
        else:
            sub_module_tracker.progress = 100
            sub_module_tracker.is_completed = True
            sub_module_tracker.completion_date = timezone.now()
        sub_module_tracker.save()
        request = {"headers": dict(self.context["request"].headers)}
        CourseProgressUpdateTask().run_task(
            db_name=get_current_db_name(), tracker=sub_module_tracker.id, request=request
        )
        return instance
