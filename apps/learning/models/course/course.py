import uuid

from django.apps import apps
from django.db import models
from django.db.models import F, Sum

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, ImageOnlyModel
from apps.forum.models import Forum, ForumCourseRelationModel
from apps.learning.communicator import chat_post_request
from apps.learning.models import BaseRoleSkillLearningModel
from apps.learning.models.common import BaseResourceModel
from config.settings import CHAT_CONFIG


class CourseImageModel(ImageOnlyModel):
    """
    Image model for Course.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class Course(BaseRoleSkillLearningModel):
    """
    Course model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image, author
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid, mml_sku_id
        Fields      - uuid, name, description, highlight, prerequisite, vm_name
        Unique      - code
        Choices     - proficiency
        Numeric     - rating, duration, certificate, learning_points, total_modules, total_sub_modules
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    TODO: Course approval part and the course proper creation flow needs to be implemented.

    """

    class Meta(BaseRoleSkillLearningModel.Meta):
        default_related_name = "related_courses"

    # ForeignKey
    image = models.ForeignKey(
        to=CourseImageModel,
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    author = models.ForeignKey("meta.Faculty", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # UUID
    mml_sku_id = models.UUIDField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # CharFields
    vm_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # NumericFields
    total_modules = models.PositiveIntegerField(default=0)
    total_sub_modules = models.PositiveIntegerField(default=0)

    @property
    def forum_as_id(self):
        """Returns the forum ids."""

        return Forum.objects.filter(related_forum_course_relations__course=self).values_list("id", flat=True)

    @property
    def file_url(self):
        """Returns the image url if available."""

        return self.image.file_url if self.image else None

    def recalculate_course_dependencies_sequence(self, assessment=False, assignment=False, from_sequence=None):
        """Called when module & assigment has been deleted & to update all the modules to new sequence."""

        instances = self.related_course_modules.order_by("sequence")
        if assessment:
            instances = self.related_course_assessments.order_by("sequence")
        elif assignment:
            instances = self.related_course_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, instance in enumerate(instances, start=1):
                instance.sequence = index
                instance.save(update_fields=["sequence"])

    def delete(self, using=None, keep_parents=False):
        """Overridden to delete the dependent modules."""

        sub_module_model = apps.get_model("learning.CourseSubModule")
        sub_module_model.objects.filter(module__course=self.pk).delete()
        self.related_course_modules.all().delete()
        instance = super().delete()
        self.role.all().role_course_count_update()
        self.skill.all().skill_course_count_update()
        self.category.category_course_count_update()
        self.dependencies_duration_count_update()
        return instance

    def course_duration_count_update(self):
        """Update the duration based on the modules."""

        tot_module = self.related_course_modules.alive()
        sub_module_model = apps.get_model("learning.CourseSubModule")
        tot_duration = tot_module.aggregate(Sum("duration"))["duration__sum"]
        self.duration = tot_duration or 0
        self.total_modules = tot_module.count()
        self.total_sub_modules = sub_module_model.objects.alive().filter(module__course=self.pk).count()
        self.save()
        self.dependencies_duration_count_update()

    def dependencies_duration_count_update(self):
        """Update the duration & course count in learning_path & skill_traveller."""

        learning_path_courses = self.related_learning_path_courses.all()
        for lp_course in learning_path_courses:
            lp_course.learning_path.duration_course_count_update()
        skill_traveller_courses = self.related_skill_traveller_courses.all()
        for st_course in skill_traveller_courses:
            st_course.skill_traveller.duration_course_count_update()

    def save(self, *args, **kwargs):
        """Overridden to update the course_code"""

        # TODO: handle the course_code generation in bulk creation of courses.
        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"COURSE_{self.pk + 1000}"
            self.save()
        return self

    def clone(self, request_headers):
        """Clone the course and related models."""

        cloned_course = Course.objects.get(pk=self.id)
        cloned_course.id = None
        cloned_course.code = None
        cloned_course.mml_sku_id = None
        cloned_course.vm_name = None
        cloned_course.uuid = uuid.uuid4()
        cloned_course.save()
        cloned_course.skill.set(self.skill.all())
        cloned_course.role.set(self.role.all())
        cloned_course.hashtag.set(self.hashtag.all())
        ForumCourseRelationModel.objects.bulk_create(
            ForumCourseRelationModel(course=cloned_course, forum=forum)
            for forum in Forum.objects.filter(related_forum_course_relations__course=self)
        )
        for catalogue in self.related_learning_catalogues.all():
            catalogue.course.add(cloned_course)
        for module in self.related_course_modules.all():
            module.clone(course_id=cloned_course.id)
        if request_headers:
            cloned_course.register_course_in_chat_service(request_headers=request_headers)
        return {"cloned_course_id": cloned_course.id}

    def register_user_to_course_in_chat(self, user_id, request_headers, user_data={}, is_expert=False):
        """Function to register user for the course in chat service."""

        # TODO: Prem / Teja Update this function for CCMS course when CCMS is Live.
        data = {
            "course_uuid": f"{self.uuid}",
            "name": self.name,
            "image": self.file_url,
            "is_ccms": False,
        }
        if is_expert:
            data["user"] = {
                "first_name": user_data.get("first_name", None),
                "last_name": user_data.get("last_name", None),
                "email": user_data.get("email", None),
                "user_id": user_data.get("user_id", None),
            }
            chat_url = CHAT_CONFIG["expert_onboard_url"]
        else:
            data["user_id"] = user_id
            chat_url = CHAT_CONFIG["course_enroll_url"]
        try:
            chat_post_request(
                url_path=chat_url,
                data=data,
                headers=request_headers,
            )
        except Exception:  # noqa
            pass

    def register_course_in_chat_service(self, request_headers):
        """Function to register the course in chat service."""

        course_chat_data = {
            "course_uuid": f"{self.uuid}",
            "name": self.name,
            "image": self.file_url,
            "is_ccms": False,
        }
        try:
            chat_post_request(
                url_path=CHAT_CONFIG["course_cud_url"],
                data=course_chat_data,
                headers=request_headers,
            )
        except Exception:  # noqa
            pass

    def update_module_sequence(self, module, to_sequence):
        """Function to update module sequences"""

        module_objs = self.related_course_modules.order_by("sequence")
        if to_sequence < module.sequence:
            module_objs = module_objs.filter(sequence__gte=to_sequence, sequence__lt=module.sequence)
            module_objs.update(sequence=F("sequence") + 1)
        else:
            module_objs = module_objs.filter(sequence__gt=module.sequence, sequence__lte=to_sequence)
            module_objs.update(sequence=F("sequence") - 1)
        module.sequence = to_sequence
        module.save()
        return True

    def report_data(self):
        """Function to return course details for report."""

        return {
            "course_id": self.id,
            "course_uuid": self.uuid,
            "course_name": self.name,
            "course_code": self.code,
            "proficiency": self.proficiency,
            "learning_points": self.learning_points,
            "duration": self.duration,
            "skills": list(self.skill.all().values_list("name", flat=True)),
        }

    @classmethod
    def ccms_report_data(cls, data):
        """Function to return ccms course details for report."""

        return {
            "course_id": data["id"],
            "course_uuid": data["uuid"],
            "course_name": data["name"],
            "course_code": data["code"],
            "proficiency": data["proficiency"],
            "learning_points": data["learning_points"],
            "duration": data["duration"],
            "skills": data["skill"],
        }


class CourseResource(BaseResourceModel):
    """
    CourseResource model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - course
        Fields      - uuid, name, description
        Choices     - type, upload_status
        Numeric     - duration,
        Datetime    - created_at, modified_at
        URL         - file_url, custom_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseResourceModel.Meta):
        default_related_name = "related_course_resources"

    # FK
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
