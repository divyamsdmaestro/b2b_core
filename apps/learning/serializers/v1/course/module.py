from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.models import Course, CourseModule
from apps.learning.serializers.v1 import CourseAssignmentListModelSerializer
from apps.learning.validators import end_date_validation

BASIC_COURSE_MODULE_FIELDS = [
    "name",
    "description",
    "start_date",
    "end_date",
    "course",
    "is_draft",
    "is_mandatory",
]


class CourseModuleCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Module serializer to perform CUD."""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive().active())

    class Meta(AppWriteOnlyModelSerializer.Meta):
        """Metaclass contains all fields in the model."""

        model = CourseModule
        fields = BASIC_COURSE_MODULE_FIELDS

    def module_date_range_validation(self, attrs):
        """Validate the dates present between the courses date."""

        course = attrs.get("course")
        course_start_date = course.start_date
        course_end_date = course.end_date
        module_start_date = attrs.get("start_date")
        module_end_date = attrs.get("end_date")
        if course_start_date and course_end_date and module_start_date and module_end_date:
            if not course_start_date <= module_start_date <= course_end_date:
                raise serializers.ValidationError(
                    {"start_date": "Module release date must be in the range of courses."}
                )
            if not course_start_date <= module_end_date <= course_end_date:
                course_date_range = f"({course_start_date} - {course_end_date})"
                raise serializers.ValidationError(
                    {"end_date": f"Module end date must be in the range of courses {course_date_range}."}
                )
        return attrs

    def module_name_unique_validation(self, course, name):
        """Validate the sequence & identity unique based on course"""

        existing_obj = course.related_course_modules.alive().filter(name=name)
        if self.instance:
            existing_obj = existing_obj.exclude(id=self.instance.pk)
        if existing_obj.exists():
            raise serializers.ValidationError({"name": "Module with this name already exists."})
        return True

    def validate(self, attrs):
        """Validate the start_date, end_date & module sequence as well."""

        attrs = super().validate(attrs)
        end_date_validation(attrs)
        self.module_date_range_validation(attrs)
        self.module_name_unique_validation(course=attrs["course"], name=attrs["name"])
        if attrs["course"].is_dependencies_sequential and not attrs["is_mandatory"]:
            raise serializers.ValidationError(
                {"is_mandatory": "Module must be mandatory due to course dependencies in sequential state."}
            )
        return attrs

    def create(self, validated_data):
        """Overridden to create modules and update duration counts."""

        course = validated_data["course"]
        max_position = course.related_course_modules.order_by("-sequence").values_list("sequence", flat=True).first()
        validated_data["sequence"] = max_position + 1 if max_position else 1
        module = super().create(validated_data=validated_data)
        module.module_duration_update()
        module.course.course_duration_count_update()
        return module

    def update(self, instance, validated_data):
        """Overridden to update the course duration."""

        instance = super().update(instance, validated_data)
        instance.course.course_duration_count_update()
        return instance

    def get_meta(self) -> dict:
        """Get meta & initial values for CourseModule."""

        return {"course": self.serialize_for_meta(Course.objects.alive(), fields=["id", "name"])}


class CourseModuleListModelSerializer(AppReadOnlyModelSerializer):
    """Course module list serializer."""

    assessments = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()
    total_sub_modules = serializers.SerializerMethodField()

    def get_assignments(self, obj):
        """Returns the related assignments."""

        assignment = obj.related_course_assignments.order_by("sequence", "created_at")
        return {"count": assignment.count(), "data": CourseAssignmentListModelSerializer(assignment, many=True).data}

    def get_assessments(self, obj):
        """Returns the assessments related to the obj."""

        assessment = obj.related_course_assessments.order_by("sequence", "created_at")
        return {"count": assessment.count(), "data": BaseIDNameSerializer(assessment, many=True).data}

    def get_total_sub_modules(self, obj):
        """Returns the no of sub modules related to the obj."""

        return obj.related_course_sub_modules.alive().count()

    class Meta:
        model = CourseModule
        fields = BASIC_COURSE_MODULE_FIELDS + [
            "id",
            "sequence",
            "duration",
            "assessments",
            "assignments",
            "total_sub_modules",
        ]


class CourseModuleRetrieveSerializer(CourseModuleListModelSerializer):
    """Retrieve serializer for modules."""

    assessments = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()

    def get_assignments(self, obj):
        """Returns the related assignments."""

        assignment = obj.related_course_assignments.order_by("sequence", "created_at")
        return {"count": assignment.count(), "data": CourseAssignmentListModelSerializer(assignment, many=True).data}

    def get_assessments(self, obj):
        """Return list of assessments based on modules."""

        return BaseIDNameSerializer(obj.related_course_assessments.order_by("sequence", "created_at"), many=True).data

    class Meta(CourseModuleListModelSerializer.Meta):
        model = CourseModule
        fields = CourseModuleListModelSerializer.Meta.fields + ["assessments"]
