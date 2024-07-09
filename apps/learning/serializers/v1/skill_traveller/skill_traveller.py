from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.common.validators import ListUniqueValidator
from apps.learning.config import JourneyTypeChoices, SkillTravellerLearningTypeChoices
from apps.learning.models import SkillTraveller, SkillTravellerCourse, SkillTravellerResource
from apps.learning.serializers.v1 import (
    BaseLearningListModelSerializer,
    BaseLearningSkillCUDModelSerializer,
    BaseLearningSkillRetrieveModelSerializer,
    CommonResourceCreateModelSerializer,
    CommonResourceListModelSerializer,
    CourseListModelSerializer,
)


class SkillTravellerCUDModelSerializer(BaseLearningSkillCUDModelSerializer):
    """Skill Traveller CUD serializer"""

    class Meta(BaseLearningSkillCUDModelSerializer.Meta):
        model = SkillTraveller
        fields = BaseLearningSkillCUDModelSerializer.Meta.fields + [
            "learning_type",
            "journey_type",
        ]

    def validate(self, attrs):
        """Overriden to validate the journey_type of the skill traveller."""

        attrs = super().validate(attrs)
        learning_type = attrs["learning_type"]
        if learning_type == SkillTravellerLearningTypeChoices.travel_journeys and not attrs.get("journey_type"):
            raise serializers.ValidationError({"journey_type": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to change the active field when the data to be save as draft."""

        validated_data["is_active"] = False
        instance = super().create(validated_data=validated_data)
        return instance

    def get_meta(self) -> dict:
        """Get meta & initial values for skill_travellers."""
        metadata = super().get_meta()
        metadata.update(
            {
                "learning_type": self.serialize_dj_choices(SkillTravellerLearningTypeChoices.choices),
                "journey_type": self.serialize_dj_choices(JourneyTypeChoices.choices),
            }
        )
        return metadata


class SkillTravellerListModelSerializer(BaseLearningListModelSerializer):
    """Skill Traveller retrieve model serializer."""

    class Meta(BaseLearningListModelSerializer.Meta):
        model = SkillTraveller
        fields = BaseLearningListModelSerializer.Meta.fields + [
            "learning_type",
            "journey_type",
            "no_of_courses",
        ]


class SkillTravellerRetrieveModelSerializer(BaseLearningSkillRetrieveModelSerializer):
    """Skill Traveller retrieve model serializer."""

    class Meta(BaseLearningSkillRetrieveModelSerializer.Meta):
        model = SkillTraveller
        fields = BaseLearningSkillRetrieveModelSerializer.Meta.fields + [
            "learning_type",
            "journey_type",
            "no_of_courses",
        ]


class SkillTravellerCourseModelListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to retrieve list of skill_traveller_courses list."""

    course = CourseListModelSerializer(read_only=True)

    class Meta:
        model = SkillTravellerCourse
        fields = [
            "id",
            "course",
            "skill_traveller",
            "sequence",
            "course_unlock_date",
            "is_mandatory",
            "is_locked",
        ]


class CourseSequenceUniqueListSerializer(serializers.ListSerializer):
    """List serializer class to validate the sequence of the course."""

    validators = [
        ListUniqueValidator(
            unique_field_names=["sequence", "course"],
            error_message={"sequence": "This sequence was already allocated.", "course": "Course is already present."},
        )
    ]


class STCourseAllocationCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for assign the courses to Skill Travellers."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = SkillTravellerCourse
        fields = [
            "course",
            "skill_traveller",
            "course_unlock_date",
            "is_mandatory",
            "is_locked",
        ]

    def validate(self, attrs):
        """Overridden to perform custom validation."""

        course, st = attrs["course"], attrs["skill_traveller"]
        is_locked, unlock_date = attrs["is_locked"], attrs["course_unlock_date"]
        st_course = st.related_skill_traveller_courses.all()
        if self.instance:
            st_course = st_course.exclude(id=self.instance.id)
        if st_course.filter(course=course).first():
            raise serializers.ValidationError({"course": "Course is already present in this Skill Traveller."})
        if is_locked and (not st.start_date or not st.end_date):
            msg = "This Skill Traveller doesn't have start date and end date specified. Hence course cannot be locked."
            raise serializers.ValidationError({"course_unlock_date": msg})
        if is_locked and not unlock_date:
            raise serializers.ValidationError({"course_unlock_date": "Unlock date is mandatory for locked courses."})
        if unlock_date and not st.start_date <= unlock_date.date() <= st.end_date:
            lp_date_range = f"{st.start_date} - {st.end_date}"
            raise serializers.ValidationError(
                {"course_unlock_date": f"Date must be within the Learning Path's schedule range ({lp_date_range})"}
            )
        return attrs

    def create(self, validated_data):
        """Overridden to update the sequence, duration & count."""

        st = validated_data["skill_traveller"]
        max_position = (
            st.related_skill_traveller_courses.order_by("-sequence").values_list("sequence", flat=True).first()
        )
        validated_data["sequence"] = max_position + 1 if max_position else 1
        instance = super().create(validated_data)
        instance.skill_traveller.duration_course_count_update()
        return instance


class SkillTravellerResourceCreateModelSerializer(CommonResourceCreateModelSerializer):
    """Serializer class to upload skill traveller resources."""

    class Meta(CommonResourceCreateModelSerializer.Meta):
        model = SkillTravellerResource
        fields = CommonResourceCreateModelSerializer.Meta.fields + ["skill_traveller"]


class SkillTravellerResourceListModelSerializer(CommonResourceListModelSerializer):
    """Serializer class to list the skill traveller resources."""

    class Meta(CommonResourceListModelSerializer.Meta):
        model = SkillTravellerResource
