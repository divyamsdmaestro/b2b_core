from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG as blank_null_config
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH as max_length
from apps.common.models import ArchivableModel


class TenantMasterReport(ArchivableModel):
    """
    Tenant wide master report table for analytics / report purposes.

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_tenant_master_reports"

    # ************************************** User ************************************************************
    user_email = models.CharField()
    user_id = models.CharField(max_length=max_length, **blank_null_config)
    user_uuid = models.CharField(max_length=max_length, **blank_null_config)
    user_username = models.CharField(max_length=max_length, **blank_null_config)
    user_first_name = models.CharField(max_length=max_length, **blank_null_config)
    user_last_name = models.CharField(max_length=max_length, **blank_null_config)
    user_status = models.BooleanField(default=False)
    # User Group Name
    user_group_names = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    user_employee_id = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Tenant ************************************************************
    tenant_id = models.CharField(max_length=max_length, **blank_null_config)
    tenant_uuid = models.CharField(max_length=max_length, **blank_null_config)
    tenant_display_name = models.CharField(max_length=max_length, **blank_null_config)
    tenant_tenancy_name = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Enrollment ************************************************************
    learning_type = models.CharField(max_length=max_length, **blank_null_config)
    approval_type = models.CharField(max_length=max_length, **blank_null_config)
    end_date = models.DateTimeField(**blank_null_config)
    is_user_group_enrollment = models.BooleanField(default=False)
    enrolled_user_group_name = models.CharField(max_length=max_length, **blank_null_config)
    # Dynamic fields from respective learning & its tracker models
    proficiency = models.CharField(max_length=max_length, **blank_null_config)
    learning_points = models.CharField(max_length=max_length, **blank_null_config)
    duration = models.CharField(max_length=max_length, **blank_null_config)
    skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    video_progress = models.PositiveIntegerField(**blank_null_config)
    start_date = models.DateField(**blank_null_config)
    completion_date = models.DateField(**blank_null_config)
    learning_status = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Course ************************************************************
    course_id = models.CharField(max_length=max_length, **blank_null_config)
    course_uuid = models.CharField(max_length=max_length, **blank_null_config)
    course_name = models.CharField(max_length=max_length, **blank_null_config)
    course_code = models.CharField(max_length=max_length, **blank_null_config)
    # course_proficiency = models.CharField(max_length=max_length, **blank_null_config)
    # course_learning_points = models.CharField(max_length=max_length, **blank_null_config)
    # course_duration = models.CharField(max_length=max_length, **blank_null_config)
    # course_skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    # course_video_progress = models.PositiveIntegerField(**blank_null_config)
    # course_start_date = models.DateField(**blank_null_config)
    # course_completion_date = models.DateField(**blank_null_config)
    # course_learning_status = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Learning Path **********************************************************
    lp_id = models.CharField(max_length=max_length, **blank_null_config)
    lp_uuid = models.CharField(max_length=max_length, **blank_null_config)
    lp_name = models.CharField(max_length=max_length, **blank_null_config)
    lp_code = models.CharField(max_length=max_length, **blank_null_config)
    # lp_proficiency = models.CharField(max_length=max_length, **blank_null_config)
    # lp_learning_points = models.CharField(max_length=max_length, **blank_null_config)
    # lp_duration = models.CharField(max_length=max_length, **blank_null_config)
    # lp_skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    # lp_video_progress = models.PositiveIntegerField(**blank_null_config)
    # lp_start_date = models.DateField(**blank_null_config)
    # lp_completion_date = models.DateField(**blank_null_config)
    # lp_learning_status = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Advanced Learning Path ***********************************************
    alp_id = models.CharField(max_length=max_length, **blank_null_config)
    alp_uuid = models.CharField(max_length=max_length, **blank_null_config)
    alp_name = models.CharField(max_length=max_length, **blank_null_config)
    alp_code = models.CharField(max_length=max_length, **blank_null_config)
    # alp_proficiency = models.CharField(max_length=max_length, **blank_null_config)
    # alp_learning_points = models.CharField(max_length=max_length, **blank_null_config)
    # alp_duration = models.CharField(max_length=max_length, **blank_null_config)
    # alp_progress = models.PositiveIntegerField(**blank_null_config)
    # alp_skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    # alp_video_progress = models.PositiveIntegerField(**blank_null_config)
    # alp_start_date = models.DateField(**blank_null_config)
    # alp_completion_date = models.DateField(**blank_null_config)
    # alp_learning_status = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Skill Traveller ***********************************************
    st_id = models.CharField(max_length=max_length, **blank_null_config)
    st_uuid = models.CharField(max_length=max_length, **blank_null_config)
    st_name = models.CharField(max_length=max_length, **blank_null_config)
    st_code = models.CharField(max_length=max_length, **blank_null_config)
    # st_proficiency = models.CharField(max_length=max_length, **blank_null_config)
    # st_learning_points = models.CharField(max_length=max_length, **blank_null_config)
    # st_duration = models.CharField(max_length=max_length, **blank_null_config)
    # st_skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    # st_video_progress = models.PositiveIntegerField(**blank_null_config)
    # st_start_date = models.DateField(**blank_null_config)
    # st_completion_date = models.DateField(**blank_null_config)
    # st_learning_status = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Assignment ***********************************************
    assignment_id = models.CharField(max_length=max_length, **blank_null_config)
    assignment_uuid = models.CharField(max_length=max_length, **blank_null_config)
    assignment_name = models.CharField(max_length=max_length, **blank_null_config)
    assignment_code = models.CharField(max_length=max_length, **blank_null_config)
    # assignment_proficiency = models.CharField(max_length=max_length, **blank_null_config)
    # assignment_learning_points = models.CharField(max_length=max_length, **blank_null_config)
    # assignment_duration = models.CharField(max_length=max_length, **blank_null_config)
    # assignment_skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    # assignment_start_date = models.DateField(**blank_null_config)
    # assignment_completion_date = models.DateField(**blank_null_config)
    # assignment_learning_status = models.CharField(max_length=max_length, **blank_null_config)
    assignment_result = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    assignment_score = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    assignment_progress = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    # ************************************** Assignment Group ***********************************************
    ag_id = models.CharField(max_length=max_length, **blank_null_config)
    ag_uuid = models.CharField(max_length=max_length, **blank_null_config)
    ag_name = models.CharField(max_length=max_length, **blank_null_config)
    ag_code = models.CharField(max_length=max_length, **blank_null_config)
    # ag_proficiency = models.CharField(max_length=max_length, **blank_null_config)
    # ag_learning_points = models.CharField(max_length=max_length, **blank_null_config)
    # ag_duration = models.CharField(max_length=max_length, **blank_null_config)
    # ag_skills = ArrayField(base_field=models.CharField(max_length=max_length), **blank_null_config)
    ag_start_date = models.DateField(**blank_null_config)
    ag_completion_date = models.DateField(**blank_null_config)
    ag_learning_status = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Skill Ontology *******************************************
    so_id = models.CharField(max_length=max_length, **blank_null_config)
    so_uuid = models.CharField(max_length=max_length, **blank_null_config)
    so_name = models.CharField(max_length=max_length, **blank_null_config)
    # ************************************** Assessment ***********************************************
    assessment_availed_attempts = models.CharField(max_length=max_length, **blank_null_config)
    assessment_progress = models.CharField(max_length=max_length, **blank_null_config)
    assessment_result = models.CharField(max_length=max_length, **blank_null_config)
    assessment_score = models.CharField(max_length=max_length, **blank_null_config)
    average_assessment_score = models.FloatField(**blank_null_config)

    def __str__(self):
        """User email has string representation."""

        return self.user_email
