from rest_framework import serializers

from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.models import (
    AdvancedLearningPath,
    Assignment,
    AssignmentGroup,
    Catalogue,
    CatalogueRelation,
    Course,
    LearningPath,
    Playground,
    PlaygroundGroup,
    SkillTraveller,
)
from apps.learning.tasks import UpdateCatalogueLearningDataTask
from apps.tenant_service.middlewares import get_current_db_name


class CatalogueCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to create catalogue."""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive(), many=True)
    learning_path = serializers.PrimaryKeyRelatedField(queryset=LearningPath.objects.alive(), many=True)
    advanced_learning_path = serializers.PrimaryKeyRelatedField(
        queryset=AdvancedLearningPath.objects.alive(), many=True
    )
    skill_traveller = serializers.PrimaryKeyRelatedField(queryset=SkillTraveller.objects.alive(), many=True)
    playground = serializers.PrimaryKeyRelatedField(queryset=Playground.objects.alive(), many=True)
    playground_group = serializers.PrimaryKeyRelatedField(queryset=PlaygroundGroup.objects.alive(), many=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.alive(), many=True)
    assignment_group = serializers.PrimaryKeyRelatedField(queryset=AssignmentGroup.objects.alive(), many=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Catalogue
        fields = [
            "name",
            "description",
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
            "playground",
            "playground_group",
            "assignment",
            "assignment_group",
            "ccms_course",
            "ccms_lp",
            "ccms_alp",
            "ccms_st",
            "ccms_tp",
            "ccms_tpg",
            "ccms_assignment",
            "is_active",
            "is_archive",
            "is_draft",
            "is_assessment_enabled",
            "is_labs_enabled",
            "is_self_enroll_enabled",
            "is_locked",
        ]

    def validate_name(self, name):
        """Overridden to validate the name with lower case."""

        existing_objs = Catalogue.objects.filter(name__iexact=name)
        if self.instance:
            existing_objs = existing_objs.exclude(id=self.instance.id)
        if existing_objs.first():
            raise serializers.ValidationError("This field must be unique.")
        return name

    def create(self, validated_data):
        """Overridden to update the count of various learning items."""

        instance = super().create(validated_data=validated_data)
        UpdateCatalogueLearningDataTask().run_task(catalogue_ids=[instance.id], db_name=get_current_db_name())
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the count of various learning items."""

        instance = super().update(instance=instance, validated_data=validated_data)
        UpdateCatalogueLearningDataTask().run_task(catalogue_ids=[instance.id], db_name=get_current_db_name())
        return instance

    def get_meta_initial(self):
        """Overridden to update the initial data with alive objects."""

        initial_data = super().get_meta_initial()
        if initial_data:
            initial_data["course"] = self.instance.course.alive().values_list("id", flat=True)
            initial_data["learning_path"] = self.instance.learning_path.alive().values_list("id", flat=True)
            initial_data["advanced_learning_path"] = self.instance.advanced_learning_path.alive().values_list(
                "id", flat=True
            )
            initial_data["skill_traveller"] = self.instance.skill_traveller.alive().values_list("id", flat=True)
            initial_data["playground"] = self.instance.playground.alive().values_list("id", flat=True)
            initial_data["playground_group"] = self.instance.playground_group.alive().values_list("id", flat=True)
            initial_data["assignment"] = self.instance.assignment.alive().values_list("id", flat=True)
            initial_data["assignment_group"] = self.instance.assignment_group.alive().values_list("id", flat=True)
        return initial_data

    def to_representation(self, instance):
        """Overridden to return a detailed representation."""

        return CatalogueRetrieveSerializer(instance).data


class CatalogueListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the catalogues."""

    created_by = SimpleUserReadOnlyModelSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Catalogue
        fields = [
            "id",
            "uuid",
            "name",
            "modified_at",
            "created_at",
            "no_of_course",
            "no_of_lp",
            "no_of_alp",
            "no_of_st",
            "no_of_tp",
            "no_of_tpg",
            "no_of_assignment",
            "no_of_assignment_group",
            "created_by",
            "is_self_enroll_enabled",
            "is_locked",
        ]


class CatalogueRetrieveSerializer(CatalogueListModelSerializer):
    """Serializer class to retrieve the catalogues."""

    course = serializers.SerializerMethodField()
    learning_path = serializers.SerializerMethodField()
    advanced_learning_path = serializers.SerializerMethodField()
    skill_traveller = serializers.SerializerMethodField()
    playground = serializers.SerializerMethodField()
    playground_group = serializers.SerializerMethodField()
    assignment = serializers.SerializerMethodField()
    assignment_group = serializers.SerializerMethodField()

    def get_course(self, obj):
        """Returns the alive courses"""

        return obj.course.alive().values_list("id", flat=True)

    def get_learning_path(self, obj):
        """Returns the alive learning_path"""

        return obj.learning_path.alive().values_list("id", flat=True)

    def get_advanced_learning_path(self, obj):
        """Returns the alive advanced_learning_path"""

        return obj.advanced_learning_path.alive().values_list("id", flat=True)

    def get_skill_traveller(self, obj):
        """Returns the alive skill_traveller"""

        return obj.skill_traveller.alive().values_list("id", flat=True)

    def get_playground(self, obj):
        """Returns the alive playground"""

        return obj.playground.alive().values_list("id", flat=True)

    def get_playground_group(self, obj):
        """Returns the alive playground_group"""

        return obj.playground_group.alive().values_list("id", flat=True)

    def get_assignment(self, obj):
        """Returns the alive assignment"""

        return obj.assignment.alive().values_list("id", flat=True)

    def get_assignment_group(self, obj):
        """Returns the alive assignment_group"""

        return obj.assignment_group.alive().values_list("id", flat=True)

    class Meta(CatalogueListModelSerializer.Meta):
        model = Catalogue
        fields = CatalogueListModelSerializer.Meta.fields + [
            "description",
            "category",
            "skill",
            "role",
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
            "playground",
            "playground_group",
            "assignment",
            "assignment_group",
            "ccms_course",
            "ccms_lp",
            "ccms_alp",
            "ccms_st",
            "ccms_tp",
            "ccms_tpg",
            "ccms_assignment",
            "is_active",
            "is_archive",
            "is_draft",
            "is_assessment_enabled",
            "is_labs_enabled",
        ]


class CatalogueRelationListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class for list catalogue relations."""

    user_group = BaseIDNameSerializer(read_only=True, many=True)
    user = BaseIDNameSerializer(read_only=True, many=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = CatalogueRelation
        fields = [
            "id",
            "uuid",
            "user_group",
            "user",
            "catalogue",
            "ccms_id",
            "is_ccms_obj",
            "created_at",
            "modified_at",
        ]


class CatalogueRelationCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for CUD of catalogue relations."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = CatalogueRelation
        fields = ["catalogue", "user_group", "user", "ccms_id", "is_ccms_obj"]

    def validate(self, attrs):
        """Overridden to validate the ccms_id field."""

        if attrs.get("is_ccms_obj"):
            attrs["catalogue"] = None
            if not attrs.get("ccms_id"):
                raise serializers.ValidationError({"ccms_id": "This field is required."})
        else:
            attrs["ccms_id"] = None
            if not attrs.get("catalogue"):
                raise serializers.ValidationError({"catalogue": "This field is required."})
        return attrs
