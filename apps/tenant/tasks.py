import uuid

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import EnrollmentTypeChoices
from apps.tenant_service.middlewares import set_db_for_router
from config.celery_app import app as celery_app


@celery_app.task
def populate_tenant_master_report_table():
    """Cron job to populate overall learning & tracker data into single table for reporting purposes."""

    print("Tenant Master Report Task - working", flush=True)
    from apps.learning.config import BaseUploadStatusChoices
    from apps.tenant_service.models import DatabaseRouter

    set_db_for_router()
    for router in DatabaseRouter.objects.filter(setup_status=BaseUploadStatusChoices.completed):
        print(f"\n** Populating Objects for {router.database_name}. **")
        MasterReportTableTask().run_task(tenant_id=router.tenant.id)
    set_db_for_router()
    print("Finished calling Tenant Master Report Task for all tenants.", flush=True)
    return True


class MasterReportTableTask(BaseAppTask):
    """Task to update playground activity and progress."""

    enrollment = None
    user = None
    is_group = None
    report = None
    learning_obj = None
    ccms_data = None
    learning_type = None
    ReportModel = None
    tenant_data = {}

    def run(self, tenant_id, **kwargs):
        """Run handler."""

        from apps.common.helpers import batch
        from apps.my_learning.models import Enrollment
        from apps.tenant.models import TenantMasterReport
        from apps.tenant_service.middlewares import set_db_for_router
        from apps.tenant_service.models import DatabaseRouter

        set_db_for_router()
        db_router = DatabaseRouter.objects.get(tenant_id=tenant_id)
        db_router.add_db_connection()
        self.tenant_data = {
            "tenant_id": f"{db_router.tenant.id}",
            "tenant_uuid": f"{db_router.tenant.uuid}",
            "tenant_display_name": f"{db_router.tenant.name}",
            "tenant_tenancy_name": f"{db_router.tenant.tenancy_name}",
        }
        set_db_for_router(db_router.database_name)
        self.switch_db(db_router.database_name)
        self.logger.info(f"Executing MasterReportTableTask on - {db_router.database_name}")

        self.ReportModel = TenantMasterReport
        self.ReportModel.objects.all().hard_delete()  # pre-processing: hard-delete everything
        for enrollment in batch(
            Enrollment.objects.filter(
                user__isnull=False,
                user_group__isnull=True,
                is_enrolled=True,
            )
        ):
            self.reset_init_values()
            self.enrollment = enrollment
            self.user = enrollment.user
            self.learning_type = enrollment.learning_type
            self.populate_enrollment_details()
        print("** User Enrollments Finished. **\n", flush=True)
        for enrollment in Enrollment.objects.filter(
            user_group__isnull=False,
            user__isnull=True,
            is_enrolled=True,
        ):
            for user in batch(enrollment.user_group.members.all()):
                self.reset_init_values()
                self.enrollment = enrollment
                self.user = user
                self.learning_type = enrollment.learning_type
                self.is_group = True
                self.populate_enrollment_details()
        print("** User Group Enrollments Finished. **\n", flush=True)
        print("** Finished Populating Master Report Table. **\n", flush=True)
        return True

    def reset_init_values(self):
        """Store default values to init variables."""

        self.enrollment = None
        self.user = None
        self.is_group = None
        self.report = None
        self.learning_obj = None
        self.learning_type = None

    def populate_enrollment_details(self):
        """Function to populate the enrollment details."""

        user_data = self.user.report_data()
        enrollment_data = self.enrollment.report_data()
        self.report = self.ReportModel.objects.create(**user_data, **enrollment_data, **self.tenant_data)
        if self.enrollment.is_ccms_obj:
            return self.populate_ccms_learning_details()
        elif getattr(self.enrollment, self.enrollment.learning_type):
            return self.populate_learning_details()

    def populate_learning_details(self):
        """Populate learning details for the user based on enrollment."""

        self.learning_obj = getattr(self.enrollment, self.enrollment.learning_type)
        data = self.enrollment.learning_tracker_report_data(
            self.enrollment.learning_type, self.learning_obj, self.user
        )
        match self.learning_type:
            case EnrollmentTypeChoices.course:
                self.update_course_data(data)
            case EnrollmentTypeChoices.learning_path:
                self.update_lp_data(data)
            case EnrollmentTypeChoices.advanced_learning_path:
                self.update_alp_data(data)
            case EnrollmentTypeChoices.skill_traveller:
                self.update_st_data(data)
            case EnrollmentTypeChoices.assignment:
                self.update_assignment_data(data)
            case EnrollmentTypeChoices.assignment_group:
                self.update_ag_data(data)
            case EnrollmentTypeChoices.skill_ontology:
                self.update_so_data(data)
            case _:  # Continue here add all learnings
                pass

    def populate_ccms_learning_details(self):
        """Populate CCMS learning details for the user based on enrollment."""

        self.ccms_data = self.enrollment.ccms_learning_data()
        if not self.ccms_data:
            return False
        data = self.enrollment.ccms_learning_tracker_report_data(
            self.enrollment.learning_type, self.ccms_data, self.user
        )
        match self.learning_type:
            case EnrollmentTypeChoices.course:
                self.update_course_data(data)
            case EnrollmentTypeChoices.learning_path:
                self.update_ccms_lp_data(data)
            case EnrollmentTypeChoices.advanced_learning_path:
                self.update_ccms_alp_data(data)
            case _:  # Continue here add all learnings
                pass

    def update_course_data(self, data):
        """Updates the report instance with course details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)

    def update_lp_data(self, data):
        """Updates the report instance with LP details & Populates related course details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        lp_report = self.ReportModel.objects.get(id=self.report.id)
        self.update_lp_or_st_course_data(lp_report, self.learning_obj.courses)

    def update_st_data(self, data):
        """Updates the report instance with Skill traveller & related course details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        st_report = self.ReportModel.objects.get(id=self.report.id)
        self.update_lp_or_st_course_data(st_report, self.learning_obj.courses)

    def update_alp_data(self, data):
        """Updates the report instance with ALP details & Populates related LP & course details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        self.update_alp_learning_path_data(self.report, self.learning_obj.learning_paths)

    def update_assignment_data(self, data):
        """Updates the report instance with assignment details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)

    def update_ag_data(self, data):
        """Updates the report instance with assignment group details & Populates related assignment details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        ag_report = self.ReportModel.objects.get(id=self.report.id)
        self.update_ag_assignment_data(ag_report, self.learning_obj.assignments)

    def update_so_data(self, data):
        """Updates the report instance with skill ontology details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        so_report = self.ReportModel.objects.get(id=self.report.id)
        self.update_so_related_learning_data(so_report)

    def update_alp_learning_path_data(self, report, lps):
        """DRY function to update alp related lps."""

        for lp in lps:
            lp_data = self.enrollment.learning_tracker_report_data(EnrollmentTypeChoices.learning_path, lp, self.user)
            lp_report = self.ReportModel.objects.get(id=report.id)
            lp_report.id = None
            lp_report.uuid = uuid.uuid4()
            lp_report.lp_id = lp_data.get("lp_id")
            lp_report.lp_uuid = lp_data.get("lp_uuid")
            lp_report.lp_name = lp_data.get("lp_name")
            lp_report.lp_code = lp_data.get("lp_code")
            self.update_report_model_fields(lp_report, lp_data)
            self.update_lp_or_st_course_data(lp_report, lp.courses)

    def update_lp_or_st_course_data(self, lp_or_st_report, courses):
        """DRY function to update lp related courses."""

        for course in courses:
            course_data = self.enrollment.learning_tracker_report_data(EnrollmentTypeChoices.course, course, self.user)
            course_report = lp_or_st_report
            course_report.id = None
            course_report.uuid = uuid.uuid4()
            course_report.course_id = course_data.get("course_id")
            course_report.course_uuid = course_data.get("course_uuid")
            course_report.course_name = course_data.get("course_name")
            course_report.course_code = course_data.get("course_code")
            self.update_report_model_fields(course_report, course_data)

    def update_ag_assignment_data(self, ag_report, assignments):
        """DRY function to update ag related assignments."""

        for assignment in assignments:
            assignment_data = self.enrollment.learning_tracker_report_data(
                EnrollmentTypeChoices.assignment, assignment, self.user
            )
            assignment_report = ag_report
            assignment_report.id = None
            assignment_report.uuid = uuid.uuid4()
            assignment_report.assignment_id = assignment_data.get("assignment_id")
            assignment_report.assignment_uuid = assignment_data.get("assignment_uuid")
            assignment_report.assignment_name = assignment_data.get("assignment_name")
            assignment_report.assignment_code = assignment_data.get("assignment_code")
            self.update_report_model_fields(assignment_report, assignment_data)

    def update_so_related_learning_data(self, so_report):
        """DRY function to update so related learnings."""

        self.update_lp_or_st_course_data(so_report, self.learning_obj.course.all())
        self.update_alp_learning_path_data(so_report, self.learning_obj.learning_path.all())
        self.update_ag_assignment_data(so_report, self.learning_obj.assignment.all())
        alps = self.learning_obj.advanced_learning_path.all()
        skill_travellers = self.learning_obj.skill_traveller.all()
        assignment_groups = self.learning_obj.assignment_group.all()
        for alp in alps:
            alp_data = self.enrollment.learning_tracker_report_data(
                EnrollmentTypeChoices.advanced_learning_path, alp, self.user
            )
            alp_report = self.ReportModel.objects.get(id=self.report.id)
            alp_report.id = None
            alp_report.uuid = uuid.uuid4()
            alp_report.alp_id = alp_data.get("alp_id")
            alp_report.alp_uuid = alp_data.get("alp_uuid")
            alp_report.alp_name = alp_data.get("alp_name")
            alp_report.alp_code = alp_data.get("alp_code")
            self.update_report_model_fields(alp_report, alp_data)
            self.update_alp_learning_path_data(alp_report, alp.learning_paths)
        for st in skill_travellers:
            st_data = self.enrollment.learning_tracker_report_data(
                EnrollmentTypeChoices.skill_traveller, st, self.user
            )
            st_report = self.ReportModel.objects.get(id=self.report.id)
            st_report.id = None
            st_report.uuid = uuid.uuid4()
            st_report.st_id = st_data.get("st_id")
            st_report.st_uuid = st_data.get("st_uuid")
            st_report.st_name = st_data.get("st_name")
            st_report.st_code = st_data.get("st_code")
            self.update_report_model_fields(st_report, st_data)
            self.update_lp_or_st_course_data(st_report, st.courses)
        for ag in assignment_groups:
            ag_data = self.enrollment.learning_tracker_report_data(
                EnrollmentTypeChoices.assignment_group, ag, self.user
            )
            ag_report = self.ReportModel.objects.get(id=self.report.id)
            ag_report.id = None
            ag_report.uuid = uuid.uuid4()
            ag_report.ag_id = ag_data.get("ag_id")
            ag_report.ag_uuid = ag_data.get("ag_uuid")
            ag_report.ag_name = ag_data.get("ag_name")
            ag_report.ag_code = ag_data.get("ag_code")
            self.update_report_model_fields(ag_report, ag_data)
            self.update_ag_assignment_data(ag_report, ag.assignments)

    def update_ccms_lp_data(self, data):
        """Updates the report instance with ccms LP details & Populates related ccms course details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        lp_report = self.ReportModel.objects.get(id=self.report.id)
        self.update_ccms_lp_course_data(lp_report, self.ccms_data["courses"])

    def update_ccms_alp_data(self, data):
        """Updates the report instance with ccms ALP details & Populates related LP & course details."""

        self.ReportModel.objects.filter(id=self.report.id).update(**data)
        self.update_ccms_alp_learning_path_data(self.report, self.ccms_data["learning_paths"])

    def update_ccms_lp_course_data(self, lp_report, courses):
        """DRY function to update ccms lp related courses."""

        for course in courses:
            course_data = self.enrollment.ccms_learning_tracker_report_data(
                EnrollmentTypeChoices.course, course, self.user
            )
            course_report = lp_report
            course_report.id = None
            course_report.uuid = uuid.uuid4()
            course_report.course_id = course_data.get("course_id")
            course_report.course_uuid = course_data.get("course_uuid")
            course_report.course_name = course_data.get("course_name")
            course_report.course_code = course_data.get("course_code")
            self.update_report_model_fields(course_report, course_data)

    def update_ccms_alp_learning_path_data(self, report, lps):
        """DRY function to update ccms alp related lps."""

        for lp in lps:
            lp_data = self.enrollment.ccms_learning_tracker_report_data(
                EnrollmentTypeChoices.learning_path, lp, self.user
            )
            lp_report = self.ReportModel.objects.get(id=report.id)
            lp_report.id = None
            lp_report.uuid = uuid.uuid4()
            lp_report.lp_id = lp_data.get("lp_id")
            lp_report.lp_uuid = lp_data.get("lp_uuid")
            lp_report.lp_name = lp_data.get("lp_name")
            lp_report.lp_code = lp_data.get("lp_code")
            self.update_report_model_fields(lp_report, lp_data)
            self.update_ccms_lp_course_data(lp_report, lp["courses"])

    @staticmethod
    def update_report_model_fields(report_model, data):
        """Updates the report model with the given kwargs."""

        report_model.proficiency = data.get("proficiency")
        report_model.learning_points = data.get("learning_points")
        report_model.duration = data.get("duration")
        report_model.skills = data.get("skills")
        report_model.video_progress = data.get("video_progress")
        report_model.start_date = data.get("start_date")
        report_model.completion_date = data.get("completion_date")
        report_model.learning_status = data.get("learning_status")
        report_model.assessment_availed_attempts = data.get("assessment_availed_attempts")
        report_model.average_assessment_score = data.get("average_assessment_score")
        report_model.assessment_progress = data.get("assessment_progress")
        report_model.assessment_result = data.get("assessment_result")
        report_model.assessment_score = data.get("assessment_score")
        report_model.assignment_result = data.get("assignment_result")
        report_model.assignment_score = data.get("assignment_score")
        report_model.assignment_progress = data.get("assignment_progress")
        report_model.save()
