from rest_framework import serializers

from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import (
    AppCreateModelSerializer,
    AppReadOnlyModelSerializer,
    AppSerializer,
    AppSpecificImageFieldSerializer,
    AppWriteOnlyModelSerializer,
    BaseIDNameSerializer,
)
from apps.forum.models import Forum
from apps.learning.config import BaseUploadStatusChoices, CourseResourceTypeChoices, ProficiencyChoices
from apps.learning.helpers import file_upload_helper
from apps.learning.models import Catalogue, Category, CategoryRole, CategorySkill
from apps.learning.tasks import UpdateCatalogueLearningDataTask
from apps.learning.validators import (
    end_date_validation,
    forum_field_validation,
    rating_field_validation,
    validate_file_size,
)
from apps.meta.models import FeedbackTemplate, Hashtag, Language
from apps.tenant_service.middlewares import get_current_db_name

BASIC_LEARNING_MODEL_LIST_FIELDS = [
    "id",
    "uuid",
    "name",
    "image",
    "code",
    "category",
    "proficiency",
    "duration",
    "rating",
    "created_by",
    "is_archive",
    "is_active",
    "is_draft",
    "is_retired",
    "retirement_date",
]

BASIC_LEARNING_MODEL_FIELDS = [
    "name",
    "code",
    "category",
    "image",
    "language",
    "hashtag",
    "description",
    "highlight",
    "prerequisite",
    "proficiency",
    "learning_points",
    "rating",
    "start_date",
    "end_date",
    "is_archive",
    "is_draft",
    "is_active",
    "is_feedback_enabled",
    "is_feedback_mandatory",
    "is_rating_enabled",
    "feedback_template",
]

BASIC_LEARNING_MODEL_CUD_FIELDS = BASIC_LEARNING_MODEL_FIELDS + [
    "forums",
    "certificate",
    "is_certificate_enabled",
    "is_forum_enabled",
    "is_assign_expert",
    "is_dependencies_sequential",
    "is_help_section_enabled",
    "is_technical_support_enabled",
    "is_popular",
    "is_trending",
    "is_recommended",
]

BASIC_LEARNING_MODEL_RETRIEVE_FIELDS = BASIC_LEARNING_MODEL_CUD_FIELDS + [
    "id",
    "uuid",
    "duration",
    "created_by",
    "created_at",
    "retirement_date",
]
talent_managements = {
    "Category": "category",
    "CategorySkill": "skill",
    "CategoryRole": "role",
}
CATALOGUE_RELATION_FIELDS = {
    "Course": "course",
    "LearningPath": "learning_path",
    "AdvancedLearningPath": "advanced_learning_path",
    "SkillTraveller": "skill_traveller",
    "Playground": "playground",
    "PlaygroundGroup": "playground_group",
    "Assignment": "assignment",
    "AssignmentGroup": "assignment_group",
    "SkillOntology": "skill_ontology",
}


class BaseCommonFieldCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Base learning common cud serializer with common fields."""

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.active(), allow_null=False, required=False)
    hashtag = serializers.ListField(
        child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, required=False)
    )
    highlight = serializers.ListField(
        source="highlight_as_list",
        child=serializers.CharField(min_length=3, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, required=False),
        default=[],
        required=False,
    )
    catalogue = serializers.PrimaryKeyRelatedField(queryset=Catalogue.objects.alive(), many=True, allow_null=True)
    feedback_template = serializers.PrimaryKeyRelatedField(
        queryset=FeedbackTemplate.objects.all(), many=True, required=False
    )

    class Meta(AppWriteOnlyModelSerializer.Meta):
        fields = BASIC_LEARNING_MODEL_FIELDS + ["catalogue"]

    def validate(self, attrs):
        """Overridden to perform custom validations."""

        end_date_validation(attrs)
        rating_field_validation(attrs)
        if hashtags := attrs.get("hashtag"):
            hashtag_ids = [Hashtag.objects.get_or_create(name=hashtag)[0].id for hashtag in hashtags]
            attrs["hashtag"] = hashtag_ids

        if attrs["is_feedback_enabled"] and not attrs.get("feedback_template"):
            raise serializers.ValidationError({"feedback_template": "This Field is required"})
        return attrs

    def get_dynamic_render_config(self):
        """Overridden to change the `highlight` field config."""

        render_config = super().get_dynamic_render_config()
        for data in render_config:
            if data["key"] == "highlight":
                data["type"] = "ArrayField"
        return render_config

    def get_meta(self) -> dict:
        """Get meta & initial values."""

        return {
            "language": self.serialize_for_meta(Language.objects.all(), fields=["id", "name"]),
            "category": self.serialize_for_meta(Category.objects.alive(), fields=["id", "name"]),
            "proficiency": self.serialize_dj_choices(ProficiencyChoices.choices),
        }

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["highlight"] = self.instance.highlight_as_list
        meta["hashtag"] = self.instance.hashtag_as_name
        meta["catalogue"] = BaseIDNameSerializer(self.instance.related_learning_catalogues.alive(), many=True).data
        return meta

    def create(self, validated_data):
        """Overridden to add the catalogue details."""

        catalogues = validated_data.pop("catalogue") or []
        instance = super().create(validated_data=validated_data)
        catalogue_ids = []
        for catalogue in catalogues:
            getattr(catalogue, CATALOGUE_RELATION_FIELDS[instance.__class__.__name__]).add(instance)
            catalogue.save()
            catalogue_ids.append(catalogue.id)
        UpdateCatalogueLearningDataTask().run_task(catalogue_ids=catalogue_ids, db_name=get_current_db_name())
        return instance

    def update(self, instance, validated_data):
        """Overridden to remove the catalogue details."""

        catalogues = validated_data.pop("catalogue") or []
        instance = super().update(instance, validated_data)
        existing_catalogues = instance.related_learning_catalogues.all()
        catalogue_ids = []
        for catalogue_obj in catalogues:
            if catalogue_obj not in existing_catalogues:
                getattr(catalogue_obj, CATALOGUE_RELATION_FIELDS[instance.__class__.__name__]).add(instance)
                catalogue_obj.save()
            catalogue_ids.append(catalogue_obj.id)
        for catalogue_obj in existing_catalogues:
            if catalogue_obj not in catalogues:
                getattr(catalogue_obj, CATALOGUE_RELATION_FIELDS[instance.__class__.__name__]).remove(instance)
                catalogue_obj.save()
            catalogue_ids.append(catalogue_obj.id)
        UpdateCatalogueLearningDataTask().run_task(catalogue_ids=catalogue_ids, db_name=get_current_db_name())
        return instance


class BaseLearningCUDModelSerializer(BaseCommonFieldCUDModelSerializer):
    """Base learning common cud serializer with boolean fields."""

    class Meta(BaseCommonFieldCUDModelSerializer.Meta):
        fields = BASIC_LEARNING_MODEL_CUD_FIELDS + ["catalogue"]

    def validate(self, attrs):
        """Validate the forum fields."""

        super().validate(attrs)
        forum_field_validation(attrs)
        return attrs

    def get_meta(self) -> dict:
        """Overridden to add the skill data."""

        metadata = super().get_meta()
        metadata.update({"forums": self.serialize_for_meta(Forum.objects.alive(), fields=["id", "name"])})
        return metadata


class BaseLearningSkillCUDModelSerializer(BaseLearningCUDModelSerializer):
    """Basic learning common cud serializer with skill."""

    skill = serializers.ListField(child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH))

    class Meta(BaseLearningCUDModelSerializer.Meta):
        fields = BaseLearningCUDModelSerializer.Meta.fields + ["skill"]

    def validate_skill(self, skill):
        """Validate the skill field required."""

        if not skill:
            raise serializers.ValidationError("This field is required.")
        return skill

    def get_meta(self) -> dict:
        """Overridden to add the skill data."""

        metadata = super().get_meta()
        metadata.update(
            {"skill": self.serialize_for_meta(queryset=CategorySkill.objects.active(), fields=["id", "name"])}
        )
        return metadata

    def skill_creation(self, category, skills):
        """
        Create if the object does not exist.
        """

        skill_ids = []
        for skill in skills:
            if existing_skill := CategorySkill.objects.filter(name=skill).first():
                skill_ids.append(existing_skill.id)
                existing_skill.category.add(category)
                continue
            skill_obj = CategorySkill.objects.get_or_create(name=skill)[0]
            skill_obj.category.add(category)
            skill_ids.append(skill_obj.id)
        return skill_ids

    def create(self, validated_data):
        """Overridden to create skill, role on the flow."""

        category = validated_data["category"]
        validated_data["skill"] = self.skill_creation(category=category, skills=validated_data.get("skill", []))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Overridden to update skill on the flow."""

        category = validated_data["category"]
        validated_data["skill"] = self.skill_creation(category=category, skills=validated_data.get("skill", []))
        return super().update(instance, validated_data)

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["skill"] = self.instance.skill.values_list("name", flat=True)
        return meta


class BaseAssignmentCUDModelSerializer(BaseCommonFieldCUDModelSerializer):
    """Base Assignment CUD model serializer."""

    skill = serializers.ListField(child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH))
    role = serializers.ListField(child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH))

    class Meta(BaseCommonFieldCUDModelSerializer.Meta):
        fields = BaseCommonFieldCUDModelSerializer.Meta.fields + ["skill", "role"]

    def skill_role_creation(self, category, skills, roles):
        """
        Create if the object does not exist.
        """

        skill_ids = []
        for skill in skills:
            if existing_skill := CategorySkill.objects.filter(name=skill).first():
                existing_skill.category.add(category)
                skill_ids.append(existing_skill.id)
                continue
            skill_obj = CategorySkill.objects.get_or_create(name=skill)[0]
            skill_obj.category.add(category)
            skill_ids.append(skill_obj.id)
        role_ids = []
        for role in roles:
            if existing_role := CategoryRole.objects.filter(name=role).first():
                existing_role.category.add(category)
                role_ids.append(existing_role.id)
                continue
            role_obj = CategoryRole.objects.get_or_create(name=role)[0]
            role_obj.category.add(category)
            role_ids.append(role_obj.id)
        return skill_ids, role_ids

    def create(self, validated_data):
        """Overridden to create skill, role on the flow."""

        category = validated_data["category"]
        validated_data["skill"], validated_data["role"] = self.skill_role_creation(
            category=category, skills=validated_data.get("skill", []), roles=validated_data.get("role", [])
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Overridden to create some necessary fields on the flow."""

        category = validated_data["category"]
        validated_data["skill"], validated_data["role"] = self.skill_role_creation(
            category=category, skills=validated_data.get("skill", []), roles=validated_data.get("role", [])
        )
        return super().update(instance, validated_data)

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["skill"] = self.instance.skill.values_list("name", flat=True)
        meta["role"] = self.instance.role.values_list("name", flat=True)
        return meta


class BaseLearningSkillRoleCUDModelSerializer(BaseLearningCUDModelSerializer, BaseAssignmentCUDModelSerializer):
    """Basic learning common cud serializer with role & skill."""

    class Meta(BaseLearningCUDModelSerializer.Meta):
        fields = BaseLearningCUDModelSerializer.Meta.fields + ["skill", "role"]


class BaseLearningListModelSerializer(AppReadOnlyModelSerializer):
    """Base learning common list model serializer."""

    category = BaseIDNameSerializer(read_only=True)
    created_by = BaseIDNameSerializer(read_only=True)
    image = AppSpecificImageFieldSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = BASIC_LEARNING_MODEL_LIST_FIELDS

    def get_filter_meta(self):
        """Returns the filter metadata."""

        category = self.serialize_for_meta(Category.objects.active(), fields=["id", "name"])
        proficiency = self.serialize_dj_choices(ProficiencyChoices.choices)
        skill = self.serialize_for_meta(CategorySkill.objects.active(), fields=["id", "name"])
        role = self.serialize_for_meta(CategoryRole.objects.active(), fields=["id", "name"])
        return {"category": category, "proficiency": proficiency, "skill": skill, "role": role}


class BaseCommonFieldRetrieveModelSerializer(AppReadOnlyModelSerializer):
    """Common retrieve model serializer."""

    category = BaseIDNameSerializer(read_only=True)
    language = BaseIDNameSerializer(read_only=True)
    created_by = BaseIDNameSerializer(read_only=True)
    hashtag = serializers.ListField(source="hashtag_as_name")
    highlight = serializers.ListField(source="highlight_as_list", read_only=True)
    catalogue = serializers.SerializerMethodField(read_only=True)
    image = AppSpecificImageFieldSerializer(read_only=True)

    def get_catalogue(self, obj):
        """Returns the catalogue the obj belongs to."""

        return BaseIDNameSerializer(obj.related_learning_catalogues.all(), many=True).data

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = BASIC_LEARNING_MODEL_FIELDS + [
            "id",
            "uuid",
            "catalogue",
            "duration",
            "created_by",
            "created_at",
            "retirement_date",
        ]


class BaseLearningRetrieveModelSerializer(BaseCommonFieldRetrieveModelSerializer):
    """Base learning common retrieve serializer."""

    class Meta(BaseCommonFieldRetrieveModelSerializer.Meta):
        fields = BASIC_LEARNING_MODEL_RETRIEVE_FIELDS + ["catalogue"]


class BaseLearningSkillRetrieveModelSerializer(BaseLearningRetrieveModelSerializer):
    """Base learning model retrieve serializer with skills."""

    skill = serializers.SerializerMethodField(read_only=True)

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    class Meta(BaseLearningRetrieveModelSerializer.Meta):
        fields = BaseLearningRetrieveModelSerializer.Meta.fields + ["skill"]


class BaseLearningSkillRoleRetrieveModelSerializer(BaseLearningRetrieveModelSerializer):
    """Base learning model retrieve serializer with skills & roles."""

    skill = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    def get_role(self, obj):
        """Returns the list of roles."""

        return obj.role.values_list("name", flat=True)

    class Meta(BaseLearningRetrieveModelSerializer.Meta):
        fields = BaseLearningRetrieveModelSerializer.Meta.fields + ["skill", "role"]


class CommonResourceCreateModelSerializer(AppCreateModelSerializer):
    """Common serializer class to upload resources."""

    # file = serializers.FileField(validators=[validate_file_extension, validate_file_size], allow_null=True)
    # TODO: Skipping validation as per @Shrini's advice along with @Darshan. (IIHT)
    file = serializers.FileField(validators=[validate_file_size], allow_null=True)
    custom_url = serializers.CharField(required=False, allow_null=True)

    class Meta(AppCreateModelSerializer.Meta):
        fields = [
            "type",
            "description",
            "custom_url",
            "file_url",
            "file",
        ]

    def validate(self, attrs):
        """Overridden to validate the resource type."""

        resource_type = attrs["type"]
        file = attrs["file"]
        if resource_type in [CourseResourceTypeChoices.video, CourseResourceTypeChoices.file] and file is None:
            raise serializers.ValidationError({"file": "This field is required."})
        return attrs

    def create(self, validated_data):
        """Overridden to upload the files in the background."""

        db_name = get_current_db_name()
        validated_data.pop("file")
        file = self.get_request().FILES.get("file", None)
        learning_type = self.context.get("learning_type")
        instance = super().create(validated_data)
        if file:
            file_upload_helper(file=file, learning_type=learning_type, db_name=db_name, instance=instance)
            instance.upload_status = BaseUploadStatusChoices.initiated
            instance.save()
        return instance

    def get_meta(self) -> dict:
        """Overridden to provide meta data"""

        return {
            "type": self.serialize_dj_choices(CourseResourceTypeChoices.choices),
        }


class CommonResourceListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the resources."""

    type = serializers.DictField(source="get_resource_type")

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = [
            "id",
            "name",
            "type",
            "description",
            "file_url",
            "custom_url",
            "upload_status",
        ]


class BaseAssignmentRetrieveModelSerializer(BaseCommonFieldRetrieveModelSerializer):
    """Base Assignment retrieve model serializer."""

    skill = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)

    def get_skill(self, obj):
        """Returns the list of skills."""

        return obj.skill.values_list("name", flat=True)

    def get_role(self, obj):
        """Returns the list of roles."""

        return obj.role.values_list("name", flat=True)

    class Meta(BaseCommonFieldRetrieveModelSerializer.Meta):
        fields = BaseCommonFieldRetrieveModelSerializer.Meta.fields + ["skill", "role"]


class BaseDependentCourseListSerializer(AppSerializer):
    """Serializer class to provide course name."""

    id = serializers.IntegerField()
    course = BaseIDNameSerializer(read_only=True)
