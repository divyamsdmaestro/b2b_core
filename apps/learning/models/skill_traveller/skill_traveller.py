import uuid
from datetime import timedelta

from django.db import models
from django.db.models import F, Sum
from django.utils import timezone

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, ImageOnlyModel
from apps.common.models.base import BaseModel
from apps.learning.config import JourneyTypeChoices, SkillTravellerLearningTypeChoices
from apps.learning.models import BaseResourceModel, BaseSkillLearningModel, Course


class SkillTravellerImageModel(ImageOnlyModel):
    """
    Image model for Skill traveller.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class SkillTraveller(BaseSkillLearningModel):
    """
    Skill traveller model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, category, language, image
        M2M         - skill, forums, hashtag, feedback_template
        UUID        - uuid
        Fields      - name, description, highlight, prerequisite,
        Unique      - code
        Choices     - proficiency, journey_type, learning_type
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

    class Meta(BaseSkillLearningModel.Meta):
        default_related_name = "related_skill_travellers"

    image = models.ForeignKey(
        to=SkillTravellerImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    learning_type = models.CharField(
        choices=SkillTravellerLearningTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    journey_type = models.CharField(
        choices=JourneyTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    no_of_courses = models.PositiveIntegerField(default=0)
    # ManyToManyField
    forums = models.ManyToManyField(to="forum.Forum", blank=True)

    def save(self, *args, **kwargs):
        """Overridden to update the Skill traveller code"""

        super().save(*args, **kwargs)
        if not self.code:
            self.code = f"ST_{self.pk + 1000}"
            self.save()

        return self

    @property
    def courses(self):
        """Returns all the associated courses."""

        from apps.learning.models.course.course import Course

        course_ids = self.related_skill_traveller_courses.all().values_list("course", flat=True)
        return Course.objects.filter(pk__in=course_ids)

    def duration_course_count_update(self):
        """Update the duration based on the assigned courses."""

        assigned_courses_pk = self.related_skill_traveller_courses.all().values_list("course")
        assigned_courses = Course.objects.filter(pk__in=assigned_courses_pk).alive()
        tot_duration = assigned_courses.aggregate(Sum("duration"))["duration__sum"]
        self.duration = tot_duration or 0
        self.no_of_courses = assigned_courses.count()
        self.save()

    def recalculate_st_course_sequence(self, from_sequence=None):
        """Called when st course has been deleted & to update all the courses to new sequence."""

        st_courses = self.related_skill_traveller_courses.order_by("sequence")
        if from_sequence:
            st_courses = st_courses.filter(sequence__gt=from_sequence)
            st_courses.update(sequence=F("sequence") - 1)
        else:
            for index, st_course in enumerate(st_courses, start=1):
                st_course.sequence = index
                st_course.save(update_fields=["sequence"])

    def recalculate_st_dependencies_sequence(self, assessment=False, assignment=False, from_sequence=None):
        """Called when st course has been deleted & to update all the courses to new sequence."""

        instances = self.related_skill_traveller_courses.order_by("sequence")
        if assessment:
            instances = self.related_st_assessments.order_by("sequence")
        elif assignment:
            instances = self.related_st_assignments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, instance in enumerate(instances, start=1):
                instance.sequence = index
                instance.save(update_fields=["sequence"])

    def clone(self):
        """Clone the ST and related models."""

        cloned_st = SkillTraveller.objects.get(pk=self.id)
        cloned_st.id = None
        cloned_st.code = None
        cloned_st.uuid = uuid.uuid4()
        cloned_st.save()
        cloned_st.skill.set(self.skill.all())
        cloned_st.forums.set(self.forums.all())
        cloned_st.hashtag.set(self.hashtag.all())
        for catalogue in self.related_learning_catalogues.all():
            catalogue.skill_traveller.add(cloned_st)
        cloned_st_courses = [
            cloned_st_course.clone(cloned_st.id) for cloned_st_course in self.related_skill_traveller_courses.all()
        ]
        return {"cloned_st_id": cloned_st.id, "cloned_st_courses": cloned_st_courses}

    def report_data(self):
        """Function to return st details for report."""

        return {
            "st_id": self.id,
            "st_uuid": self.uuid,
            "st_name": self.name,
            "st_code": self.code,
            "proficiency": self.proficiency,
            "learning_points": self.learning_points,
            "duration": self.duration,
            "skills": list(self.skill.all().values_list("name", flat=True)),
        }


class SkillTravellerCourse(BaseModel):
    """
    Course Model related to Skill Traveller.

    Model Fields -

        PK          - id,
        Fk          - skill_traveller, course
        Numeric     - sequence
        Date        - course_unlock_date
        Datetime    - created_at, modified_at
        Bool        - is_mandatory, is_locked

    App QuerySet Manager Methods -
        get_or_none

    """

    class Meta:
        default_related_name = "related_skill_traveller_courses"

    skill_traveller = models.ForeignKey(to=SkillTraveller, on_delete=models.CASCADE)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
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
            and timezone.now().date() < (self.course_unlock_date + timedelta(hours=5, minutes=30))
        ):
            return True
        return False

    def delete(self, using=None, keep_parents=False):
        """Overridden to update the skill_traveller course count when the course is deleted."""

        instance = super().delete()
        self.skill_traveller.duration_course_count_update()
        self.skill_traveller.recalculate_st_course_sequence(from_sequence=self.sequence)
        return instance

    def recalculate_st_course_dependencies_sequence(self, assignment=False, from_sequence=None):
        """
        Called when st_course dependencies has been deleted & to update all the dependencies to new sequence.
        """

        if assignment:
            instances = self.related_st_assignments.order_by("sequence")
        else:
            instances = self.related_st_assessments.order_by("sequence")
        if from_sequence:
            instances = instances.filter(sequence__gt=from_sequence)
            instances.update(sequence=F("sequence") - 1)
        else:
            for index, instance in enumerate(instances, start=1):
                instance.sequence = index
                instance.save(update_fields=["sequence"])

    def clone(self, skill_traveller_id):
        """Clone the LP course."""

        cloned_stc = SkillTravellerCourse.objects.get(pk=self.id)
        cloned_stc.id = None
        cloned_stc.skill_traveller_id = skill_traveller_id
        cloned_stc.uuid = uuid.uuid4()
        cloned_stc.save()
        return {"cloned_lp_course_id": cloned_stc.id}


class SkillTravellerResource(BaseResourceModel):
    """
    SkillTravellerResource model for IIHT-B2B.

    Model Fields -
        PK          - id,
        Fk          - skill_traveller
        Fields      - uuid, name, description
        Choices     - type
        Numeric     - duration, upload_status
        Datetime    - created_at, modified_at
        URL         - file_url, custom_url

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseResourceModel.Meta):
        default_related_name = "related_skill_traveller_resources"

    # FK
    skill_traveller = models.ForeignKey(to=SkillTraveller, on_delete=models.CASCADE)
