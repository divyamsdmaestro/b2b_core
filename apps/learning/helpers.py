import os

from django.db import transaction
from django_filters import rest_framework as filters

from apps.common.cache_management import cache_manager
from apps.common.communicator import get_request
from apps.common.helpers import process_request_headers
from apps.common.idp_service import idp_admin_auth_token
from apps.learning.config import AssignmentTypeChoices, PlaygroundToolChoices, ProficiencyChoices
from apps.learning.models import (
    AdvancedLearningPath,
    Assignment,
    AssignmentGroup,
    AssignmentSubTopic,
    AssignmentTopic,
    Category,
    CategoryRole,
    CategorySkill,
    Course,
    LearningPath,
    Playground,
    PlaygroundGroup,
    SkillTraveller,
)
from apps.learning.tasks import ResourceUploadTask, ScormUploadTask
from apps.my_learning.config import AllBaseLearningTypeChoices, EnrollmentTypeChoices
from config.settings import IDP_CONFIG

CCMS_URL_RELATED_KEYS = {
    EnrollmentTypeChoices.course: "course",
    EnrollmentTypeChoices.learning_path: "learning-path",
    EnrollmentTypeChoices.advanced_learning_path: "advanced-learning-path",
    EnrollmentTypeChoices.skill_traveller: "skill-traveller",
    EnrollmentTypeChoices.playground: "playground",
    EnrollmentTypeChoices.playground_group: "playground-group",
    EnrollmentTypeChoices.assignment: "assignment",
    "assignment_core": "assignment/core",
    "catalogue": "catalogue",
    "course_module": "course/module",
    "course_submodule": "course/submodule",
    "core_submodule": "course/submodule/core",
    "course_assessment": "course/assessment",
    "course_assignment": "course/assignment",
    "core_course": "course/core",
    "core_learning_path": "learning-path/core",
    "core_advanced_learning_path": "advanced-learning-path/core",
    "lp_course": "learning-path/course",
    "lp_assessment": "learning-path/assessment",
    "lp_assignment": "learning-path/assignment",
    "lp_core_course": "learning-path/core/course",
    "alp_lp": "advanced-learning-path/learning-path",
    "alp_core_lp": "advanced-learning-path/core/learning-path",
    "feedback": "meta/feedback/core",
    "common_learning": "common/learning",
}

LEARNING_INSTANCE_MODELS = {
    AllBaseLearningTypeChoices.course: Course,
    AllBaseLearningTypeChoices.learning_path: LearningPath,
    AllBaseLearningTypeChoices.advanced_learning_path: AdvancedLearningPath,
    AllBaseLearningTypeChoices.skill_traveller: SkillTraveller,
    AllBaseLearningTypeChoices.playground: Playground,
    AllBaseLearningTypeChoices.playground_group: PlaygroundGroup,
    AllBaseLearningTypeChoices.assignment: Assignment,
    AllBaseLearningTypeChoices.assignment_group: AssignmentGroup,
}


def process_and_save_uploaded_file(file, folder_path):
    """Stores the uploaded file locally for background upload purpose."""

    upload_file = file.chunks()
    # store the file to the project folder
    file_path = os.path.join(folder_path, file.name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb+") as f:
        for chunk in upload_file:
            f.write(chunk)
    return file_path


def file_upload_helper(file, learning_type, db_name, instance):
    """Stores the uploaded file locally for background upload purpose and then calls the task to upload to Azure."""

    from django.db import transaction

    file_name = file.name
    upload_file = file.chunks()
    # store the file to the project folder
    folder_path = f"apps/media/temp/{db_name}/{learning_type}/resource"
    file_path = os.path.join(folder_path, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb+") as f:
        for chunk in upload_file:
            f.write(chunk)
    # task to upload the file to Django default storage
    # ref: https://docs.djangoproject.com/en/5.0/topics/db/transactions/#django.db.transaction.on_commit
    transaction.on_commit(
        lambda: ResourceUploadTask().run_task(
            resource_file_path=file_path,
            filename=file_name,
            db_name=db_name,
            resource_pk=instance.pk,
            learning_type=learning_type,
            resource_type=instance.type,
        )
    )


def scorm_upload_helper(file, db_name, instance_id):
    """
    Stores the uploaded scorm file locally for background upload purpose and then calls the task to upload to Azure.
    """

    file_name = file.name
    upload_file = file.chunks()
    # store the file to the project folder
    folder_path = f"apps/media/temp/{db_name}/scorm"
    file_path = os.path.join(folder_path, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb+") as f:
        for chunk in upload_file:
            f.write(chunk)
    # task to upload the scorm file to Django default storage
    transaction.on_commit(
        lambda: ScormUploadTask().run_task(
            file_path=file_path, file_name=file_name, db_name=db_name, scorm_pk=instance_id
        )
    )


class CommonMultipleChoiceFilter(filters.FilterSet):
    """Filter class to support multiple choices."""

    id = filters.AllValuesMultipleFilter(field_name="id")
    category = filters.ModelMultipleChoiceFilter(field_name="category", queryset=Category.objects.alive())
    proficiency = filters.MultipleChoiceFilter(field_name="proficiency", choices=ProficiencyChoices.choices)
    is_trending = filters.BooleanFilter(field_name="is_trending")
    is_popular = filters.BooleanFilter(field_name="is_popular")
    is_recommended = filters.BooleanFilter(field_name="is_recommended")
    created_at = filters.DateTimeFilter(field_name="created_at")
    code = filters.AllValuesMultipleFilter(field_name="code")

    class Meta:
        fields = [
            "id",
            "category",
            "proficiency",
            "created_at",
            "is_trending",
            "is_popular",
            "is_recommended",
            "code",
        ]


class BaseLearningSkillRoleFilter(CommonMultipleChoiceFilter):
    """Filter class to support multiple choices for `BaseLearningSkillRole` model."""

    skill = filters.ModelMultipleChoiceFilter(field_name="skill", queryset=CategorySkill.objects.alive())
    role = filters.ModelMultipleChoiceFilter(field_name="role", queryset=CategoryRole.objects.alive())

    class Meta(CommonMultipleChoiceFilter.Meta):
        fields = CommonMultipleChoiceFilter.Meta.fields + [
            "skill",
            "role",
        ]


class AssignmentFilter(BaseLearningSkillRoleFilter):
    """Filter class to support multiple choices for `Assignment` model."""

    topic = filters.ModelMultipleChoiceFilter(field_name="topic", queryset=AssignmentTopic.objects.all())
    subtopic = filters.ModelMultipleChoiceFilter(field_name="subtopic", queryset=AssignmentSubTopic.objects.all())
    type = filters.MultipleChoiceFilter(field_name="type", choices=AssignmentTypeChoices.choices)
    tool = filters.MultipleChoiceFilter(field_name="tool", choices=PlaygroundToolChoices.choices)

    class Meta(BaseLearningSkillRoleFilter.Meta):
        fields = BaseLearningSkillRoleFilter.Meta.fields + [
            "type",
            "topic",
            "subtopic",
            "tool",
        ]


def get_ccms_retrieve_details(request, learning_type, instance_id, params={}, is_default_creds=False, use_cache=False):
    """Returns the ccms details based on type."""

    url_path = f"api/v1/{CCMS_URL_RELATED_KEYS.get(learning_type)}/detail/{instance_id}/"
    if use_cache:
        if cached_data := cache_manager.get_item_in_cache(url_path):
            return True, cached_data
    if is_default_creds:
        idp_token = idp_admin_auth_token(raise_drf_error=False)
        headers = {"Token": idp_token, "Issuer": "IDP", "Issuer-Url": IDP_CONFIG["host"]}
    else:
        headers = process_request_headers(request)
    success, data = get_request(
        service="CCMS",
        url_path=url_path,
        params=params,
        headers=headers,
    )
    if use_cache and success:
        cache_manager.set_item_in_cache(item=url_path, value=data)
    return success, data


def convert_hms_to_sec(hms_string):
    """Convert 'HH:MM:SS' format to seconds."""

    try:
        hours, minutes, seconds = map(int, hms_string.split(":"))
        return hours * 3600 + minutes * 60 + seconds
    except Exception:
        return None
