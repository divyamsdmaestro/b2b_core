from djchoices import ChoiceItem, DjangoChoices


class MailTypeChoices(DjangoChoices):
    """Holds the mail type choices."""

    learner_welcome = ChoiceItem("learner_welcome", "Learner Welcome Email")
    course_completion = ChoiceItem("course_completion", "Course Completion")
    course_self_enrollment = ChoiceItem("course_self_enrollment", "Course Self-Enrollment")
    course_admin_assign = ChoiceItem("course_admin_assign", "Course Assigned By Admin or Manager")
    lp_self_enrollment = ChoiceItem("lp_self_enrollment", "LP Self-enrollment")
    lp_admin_assign = ChoiceItem("lp_admin_assign", "LP - Admin Assign")
    lp_completion = ChoiceItem("lp_completion", "LP - Completion")
    alp_self_enrollment = ChoiceItem("alp_self_enrollment", "ALP Self-enrollment")
    alp_admin_assign = ChoiceItem("alp_admin_assign", "ALP - Assigned")
    alp_completion = ChoiceItem("alp_completion", "ALP - Completion")
    enrollment_expiration = ChoiceItem("enrollment_expiration", "Enrollment Expiration")
    password_reset = ChoiceItem("password_reset", "Password Reset")
    unenrollment = ChoiceItem("unenrollment", "Unenrollment")
    bulk_unenrollment = ChoiceItem("bulk_unenrollment", "Bulk Unenrollment")
    assignment_upload = ChoiceItem("assignment_upload", "Assignment Upload")
    user_assignment_upload = ChoiceItem("user_assignment_upload", "User Assignment Upload")
    user_invite = ChoiceItem("user_invite", "User Invite")
    enrollment_request = ChoiceItem("enrollment_request", "Enrollment Request")
    scorm_upload = ChoiceItem("scorm_upload", "Scorm Upload")
    report_trigger = ChoiceItem("report_trigger", "Report Trigger")
    assignment_self_enrollment = ChoiceItem("assignment_self_enrollment", "Assignment Self-enrollment")
    assignment_admin_assign = ChoiceItem("assignment_admin_assign", "Assignment - Assigned")
    certification_mail = ChoiceItem("certification_mail", "Certification Mail")


class TemplateFieldChoices(DjangoChoices):
    """Holds the mail template's dynamic keys choices."""

    user_name = ChoiceItem("user_name", "{{user_name}}")
    user_email = ChoiceItem("user_email", "{{user_email}}")
    website_url = ChoiceItem("website_url", "{{website_url}}")
    user_password = ChoiceItem("user_password", "{{user_password}}")
    user_role = ChoiceItem("user_role", "{{user_role}}")
    artifact_type = ChoiceItem("artifact_type", "{{artifact_type}}")
    artifact_name = ChoiceItem("artifact_name", "{{artifact_name}}")
    artifact_progress = ChoiceItem("artifact_progress", "{{artifact_progress}}")
    completion_date = ChoiceItem("completion_date", "{{completion_date}}")
    end_date = ChoiceItem("end_date", "{{end_date}}")


MAIL_DYNAMIC_FIELDS = {
    MailTypeChoices.learner_welcome: {
        "required": [
            TemplateFieldChoices.labels.user_name,
            TemplateFieldChoices.labels.website_url,
            TemplateFieldChoices.labels.user_email,
            TemplateFieldChoices.labels.user_password,
        ],
        "optional": [TemplateFieldChoices.labels.user_role],
    },
    MailTypeChoices.course_self_enrollment: {
        "required": [
            TemplateFieldChoices.labels.user_name,
            TemplateFieldChoices.labels.website_url,
            TemplateFieldChoices.labels.artifact_name,
        ],
        "optional": [],
    },
    MailTypeChoices.course_completion: {
        "required": [
            TemplateFieldChoices.labels.user_name,
            TemplateFieldChoices.labels.artifact_name,
            TemplateFieldChoices.labels.website_url,
        ],
        "optional": [TemplateFieldChoices.labels.completion_date],
    },
    MailTypeChoices.unenrollment: {
        "required": [
            TemplateFieldChoices.labels.user_name,
            TemplateFieldChoices.labels.artifact_type,
            TemplateFieldChoices.labels.artifact_name,
            TemplateFieldChoices.labels.website_url,
        ],
        "optional": [],
    },
    MailTypeChoices.enrollment_expiration: {
        "required": [
            TemplateFieldChoices.labels.user_name,
            TemplateFieldChoices.labels.artifact_type,
            TemplateFieldChoices.labels.artifact_name,
            TemplateFieldChoices.labels.artifact_progress,
            TemplateFieldChoices.labels.end_date,
            TemplateFieldChoices.labels.website_url,
        ],
        "optional": [],
    },
}
MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_admin_assign] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_self_enrollment]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.lp_self_enrollment] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_self_enrollment]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.lp_admin_assign] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_self_enrollment]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.lp_completion] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_completion]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.alp_self_enrollment] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_self_enrollment]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.alp_admin_assign] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_self_enrollment]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.alp_completion] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_completion]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.certification_mail] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_completion]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.report_trigger] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_completion]
MAIL_DYNAMIC_FIELDS[MailTypeChoices.user_assignment_upload] = MAIL_DYNAMIC_FIELDS[MailTypeChoices.course_completion]
