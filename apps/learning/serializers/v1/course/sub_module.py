from rest_framework import serializers

from apps.access.models import User
from apps.access_control.config import RoleTypeChoices
from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.learning.config import BaseUploadStatusChoices, EvaluationTypeChoices, SubModuleTypeChoices
from apps.learning.helpers import file_upload_helper
from apps.learning.models import CourseModule
from apps.learning.models.course.sub_module import CourseSubModule
from apps.learning.serializers.v1 import CommonResourceListModelSerializer
from apps.learning.validators import allowed_file_ext_validator, validate_file_size
from apps.tenant_service.middlewares import get_current_db_name


class CourseSubModuleCUDSerializer(AppWriteOnlyModelSerializer):
    """SubModule model serializer to perform CUD."""

    module = serializers.PrimaryKeyRelatedField(queryset=CourseModule.objects.alive())
    file = serializers.FileField(validators=[allowed_file_ext_validator, validate_file_size], allow_null=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(roles__role_type=RoleTypeChoices.author), many=True, required=False
    )

    class Meta(AppWriteOnlyModelSerializer.Meta):
        """Metaclass contains required fields in the model."""

        model = CourseSubModule
        fields = [
            "name",
            "description",
            "type",
            "custom_url",
            "file_url",
            "file",
            "duration",
            "is_draft",
            "module",
            "evaluation_type",
            "author",
        ]

    def validate(self, attrs):
        """Validate the start_date, end_date & module sequence as well."""

        attrs = super().validate(attrs)
        self.custom_unique_together_validation(attrs)
        resource_type = attrs["type"]
        file = attrs["file"]
        if ((self.instance and self.instance.type != resource_type) or not self.instance) and resource_type in [
            SubModuleTypeChoices.video,
            SubModuleTypeChoices.file,
            SubModuleTypeChoices.file_submission,
        ]:
            attrs["custom_url"] = None
            if file is None:
                raise serializers.ValidationError({"file": "This field is required."})
        elif resource_type == SubModuleTypeChoices.custom_url:
            if attrs["duration"] is None:
                raise serializers.ValidationError({"duration": "This field is required."})
            if attrs["custom_url"] is None:
                raise serializers.ValidationError({"custom_url": "This field is required."})
        if resource_type == SubModuleTypeChoices.file_submission and not attrs.get("evaluation_type"):
            raise serializers.ValidationError({"evaluation_type": "This field is required."})
        return attrs

    def custom_unique_together_validation(self, attrs):
        """Validate the sequence & identity unique based on module"""

        instance = self.instance
        module = attrs.get("module")
        name = attrs.get("name")
        existing_obj = module.related_course_sub_modules.alive().exclude(pk=instance.pk if instance else None)
        name_existing_obj = existing_obj.filter(name=name).first()
        if name_existing_obj:
            raise serializers.ValidationError({"name": "SubModule with this name already exists."})
        return True

    def create(self, validated_data):
        """Overridden to update the duration of module & course."""

        # File Pre-processing
        db_name = get_current_db_name()
        validated_data.pop("file")
        file = self.get_request().FILES.get("file", None)
        learning_type = self.context.get("learning_type")
        # Position Auto Populate
        module = validated_data["module"]
        max_position = (
            module.related_course_sub_modules.order_by("-sequence").values_list("sequence", flat=True).first()
        )
        validated_data["sequence"] = max_position + 1 if max_position else 1
        instance = super().create(validated_data)
        if file and instance.type in [
            SubModuleTypeChoices.video,
            SubModuleTypeChoices.file,
            SubModuleTypeChoices.file_submission,
        ]:
            file_upload_helper(file=file, learning_type=learning_type, db_name=db_name, instance=instance)
            instance.upload_status = BaseUploadStatusChoices.initiated
            instance.save()
        instance.duration_update()
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the duration of module & course."""

        # File Pre-processing
        db_name = get_current_db_name()
        validated_data.pop("file")
        file = self.get_request().FILES.get("file", None)
        learning_type = self.context.get("learning_type")
        instance = super().update(instance, validated_data)
        if file and instance.type in [
            SubModuleTypeChoices.video,
            SubModuleTypeChoices.file,
            SubModuleTypeChoices.file_submission,
        ]:
            file_upload_helper(file=file, learning_type=learning_type, db_name=db_name, instance=instance)
            instance.upload_status = BaseUploadStatusChoices.initiated
            instance.save()
        instance.duration_update()
        return instance

    def get_meta(self) -> dict:
        """Get meta &  initial_data"""

        return {
            "type": self.serialize_dj_choices(SubModuleTypeChoices.choices),
            "evaluation_type": self.serialize_dj_choices(EvaluationTypeChoices.choices),
        }

    def get_meta_initial(self):
        """Returns the initial data."""

        initial_data = super().get_meta_initial()
        initial_data.update({"upload_status": self.instance.upload_status})
        return initial_data


class CourseSubModuleListSerializer(CommonResourceListModelSerializer):
    """Retrieve serializer for sub modules"""

    class Meta(CommonResourceListModelSerializer.Meta):
        model = CourseSubModule
        fields = CommonResourceListModelSerializer.Meta.fields + [
            "sequence",
            "duration",
            "is_draft",
            "module",
            "evaluation_type",
            "author",
        ]
