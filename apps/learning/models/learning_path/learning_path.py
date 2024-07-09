import uuid
from datetime import timedelta

from django.apps import apps
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel, ImageOnlyModel
from apps.learning.models import BaseResourceModel, LearningPathCommonModel


class LearningPathImageModel(ImageOnlyModel):
    """
    Image model for learning paths.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class LearningPath(LearningPathCommonModel):
    """
    Learning path model for IIHT-B2B.

    Model Fields -

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image
        M2M         - skill, role, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency, learning_type
        Numeric     - rating, duration, certificate, learning_points, no_of_courses
        Date        - start_date, end_date
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_archive, is_draft, is_certificate_enabled, is_feedback_enabled, is_feedback_mandatory,
                      is_rating_enabled, is_forum_enabled, is_assign_expert, is_dependencies_sequential,
                      is_help_section_enabled, is_technical_support_enabled,
                      is_popular, is_trending, is_recommended,

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(LearningPathCommonModel.Meta):
        default_related_name = "related_learning_paths"

    # FK
    image = models.ForeignKey(
        to=LearningPathImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    forums = models.ManyToManyField(to="forum.Forum", blank=True)

    # Numeric
    no_of_courses = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        """Overridden to update the course_code"""

        # TODO: handle the course_code generation in bulk creation of courses.
        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"LP_{self.pk + 1000}"
            self.save()

        return self

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the role, category & skills learning_path counts when the lp is deleted."""

        instance = super().delete()
        self.role.all().role_learning_path_count_update()
        self.skill.all().skill_learning_path_count_update()
        self.category.category_learning_path_count_update()

        return instance

    @property
    def courses(self):
        """Returns all the associated courses."""

        from apps.learning.models.course.course import Course

        course_ids = self.related_learning_path_courses.all().values_list("course")
        return Course.objects.filter(pk__in=course_ids)

    def duration_course_count_update(self):
        """Update the duration based on the assigned courses."""

        CourseKlass = apps.get_model("learning.Course")
        assigned_courses_pk = self.related_learning_path_courses.all().values_list("course")
        assigned_courses = CourseKlass.objects.filter(pk__in=assigned_courses_pk).alive()
        tot_duration = assigned_courses.aggregate(Sum("duration"))["duration__sum"]
        self.duration = tot_duration or 0
        self.no_of_courses = assigned_courses.count()
        self.save()

    def recalculate_lp_dependencies_sequence(self, assessment=False, assignment=False, from_sequence=None):
        """Called when lp course has been deleted & to update all the courses to new sequence."""

        instances = self.related_learning_path_courses.order_by("sequence")
        if assessment:
            instances = self.related_lp_assessments.order_by("sequence")
        elif assignment:
            instances = self.related_lp_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, lp_course in enumerate(instances, start=1):
                lp_course.sequence = index
                lp_course.save(update_fields=["sequence"])

    def clone(self):
        """Clone the LP and related models."""

        cloned_lp = LearningPath.objects.get(pk=self.id)
        cloned_lp.id = None
        cloned_lp.code = None
        cloned_lp.uuid = uuid.uuid4()
        cloned_lp.save()
        cloned_lp.skill.set(self.skill.all())
        cloned_lp.role.set(self.role.all())
        cloned_lp.forums.set(self.forums.all())
        cloned_lp.hashtag.set(self.hashtag.all())
        for catalogue in self.related_learning_catalogues.all():
            catalogue.learning_path.add(cloned_lp)
        cloned_lp_courses = [
            cloned_lp_course.clone(cloned_lp.id) for cloned_lp_course in self.related_learning_path_courses.all()
        ]
        return {"cloned_lp_id": cloned_lp.id, "cloned_lp_courses": cloned_lp_courses}

    def report_data(self):
        """Function to return lp details for report."""

        return {
            "lp_id": self.id,
            "lp_uuid": self.uuid,
            "lp_name": self.name,
            "lp_code": self.code,
            "proficiency": self.proficiency,
            "learning_points": self.learning_points,
            "duration": self.duration,
            "skills": list(self.skill.all().values_list("name", flat=True)),
        }

    @classmethod
    def ccms_report_data(cls, data):
        """Function to return ccms lp details for report."""

        return {
            "lp_id": data["id"],
            "lp_uuid": data["uuid"],
            "lp_name": data["name"],
            "lp_code": data["code"],
            "proficiency": data["proficiency"],
            "learning_points": data["learning_points"],
            "duration": data["duration"],
            "skills": data["skill"],
        }


class LearningPathCourse(BaseModel):
    """
    Course Model related to learning path.

    Model Fields -

        PK          - id,
        Fk          - learning_path, course
        Numeric     - sequence
        Date        - course_unlock_date
        Datetime    - created_at, modified_at
        Bool        - is_mandatory, is_locked

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta:
        default_related_name = "related_learning_path_courses"

    learning_path = models.ForeignKey(to=LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey(to="learning.Course", on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    course_unlock_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    is_mandatory = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    @property
    def is_lock_active(self):
        """Returns the status of the lock."""

        if (
            self.is_locked
            and self.course_unlock_date
            and timezone.now() < (self.course_unlock_date + timedelta(hours=5, minutes=30))
        ):
            return True
        return False

    def recalculate_lp_course_dependencies_sequence(self, assignment=False, from_sequence=None):
        """
        Called when lp_course dependencies has been deleted & to update all the dependencies to new sequence.
        """

        instances = self.related_lp_assessments.order_by("sequence")
        if assignment:
            instances = self.related_lp_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, lp_course in enumerate(instances, start=1):
                lp_course.sequence = index
                lp_course.save(update_fields=["sequence"])

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the learning_path course count when the course is deleted."""

        instance = super().delete()
        self.learning_path.duration_course_count_update()
        self.learning_path.recalculate_lp_dependencies_sequence(from_sequence=self.sequence)
        return instance

    def clone(self, learning_path_id):
        """Clone the LP course."""

        cloned_lpc = LearningPathCourse.objects.get(pk=self.id)
        cloned_lpc.id = None
        cloned_lpc.learning_path_id = learning_path_id
        cloned_lpc.uuid = uuid.uuid4()
        cloned_lpc.save()
        return {"cloned_lp_course_id": cloned_lpc.id}


class LearningPathResource(BaseResourceModel):
    """
    LearningPathResource model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - learning_path
        Fields      - uuid, name, description
        Choices     - type, upload_status
        Numeric     - duration,
        Datetime    - created_at, modified_at
        URL         - file_url, custom_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseResourceModel.Meta):
        default_related_name = "related_learning_path_resources"

    # FK
    learning_path = models.ForeignKey(to=LearningPath, on_delete=models.CASCADE)
