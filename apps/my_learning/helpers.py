from django.utils import timezone

from apps.common.communicator import get_request
from apps.common.helpers import process_request_headers
from apps.leaderboard.config import BadgeCategoryChoices, MilestoneChoices
from apps.leaderboard.tasks import CommonBadgeTask, CommonLeaderboardTask
from apps.learning.config import AssessmentTypeChoices, PlaygroundToolChoices
from apps.learning.helpers import CCMS_URL_RELATED_KEYS
from apps.meta.models import MMLConfiguration, YakshaConfiguration
from apps.my_learning.config import BaseLearningTypeChoices, EnrollmentTypeChoices
from apps.my_learning.serializers.v1 import LEARNING_RELATED_FIELDS, tracker_related_fields
from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_idp_id

RELATED_TRACKER_NAMES = {
    EnrollmentTypeChoices.course: "related_user_course_trackers",
    EnrollmentTypeChoices.learning_path: "related_user_learning_path_trackers",
    EnrollmentTypeChoices.advanced_learning_path: "related_user_alp_trackers",
    EnrollmentTypeChoices.skill_traveller: "related_user_skill_traveller_trackers",
    EnrollmentTypeChoices.assignment: "related_assignment_trackers",
    EnrollmentTypeChoices.assignment_group: "related_assignment_group_trackers",
    EnrollmentTypeChoices.skill_ontology: "related_user_skill_ontology_trackers",
}

RELATED_ASSESSMENT_NAMES = {
    EnrollmentTypeChoices.course: "related_course_assessments",
    EnrollmentTypeChoices.learning_path: "related_lp_assessments",
    EnrollmentTypeChoices.advanced_learning_path: "related_alp_assessments",
}

RELATED_ASSIGNMENT_NAMES = {
    EnrollmentTypeChoices.course: "related_course_assignments",
    EnrollmentTypeChoices.learning_path: "related_lp_assignments",
    EnrollmentTypeChoices.advanced_learning_path: "related_alp_assignments",
}


def assignment_config_detail(assignment_id, enrollment, choice):
    """Returns the configuration details for yaksha or mml for assignments."""

    learning_instance = getattr(enrollment, enrollment.learning_type)
    if choice == PlaygroundToolChoices.yaksha:
        model = YakshaConfiguration
        related_configs = getattr(learning_instance, "related_yaksha_configurations", None)
    else:
        model = MMLConfiguration
        related_configs = getattr(learning_instance, "related_mml_configurations", None)
    if enrollment.is_ccms_obj:
        return model.objects.filter(is_default=True).first()
    related_catalogs = getattr(learning_instance, "related_learning_catalogues", None)
    if not related_configs or not related_catalogs:
        return model.objects.filter(is_default=True).first()
    config = (
        model.objects.filter(assignment_id=assignment_id)
        or related_configs.all()
        or model.objects.filter(catalogue__in=related_catalogs.values_list("id", flat=True))
        or model.objects.filter(is_default=True)
    ).first()
    return config


def assessment_config_detail(instance_key, instance, is_practice=False, is_ccms_obj=False):
    """Returns the yaksha configuration."""

    yaksha_instance = YakshaConfiguration.objects.filter(is_practice=is_practice)
    if is_ccms_obj or not instance_key or not instance:
        config = yaksha_instance.filter(is_default=True).first()
    else:
        config = (
            yaksha_instance.filter(**{instance_key: instance})
            or instance.related_yaksha_configurations.all()
            or yaksha_instance.filter(catalogue__in=instance.related_learning_catalogues.values_list("id", flat=True))
            or yaksha_instance.filter(is_default=True)
        ).first()
    return config


def get_yaksha_config(config_instance, learning_type, learning_id, assessment_type, assessment_id, is_ccms_obj):
    """Returns the yaksha configuration."""

    custom_args = {
        "learning_type": learning_type,
        "learning_id": learning_id,
        "assessment_type": assessment_type,
        "assessment_id": assessment_id,
        "is_ccms_obj": is_ccms_obj,
        "tenant_id": get_current_tenant_idp_id(),
        "CourseId": 0,
        "LearningPathId": 0,
        "CertificationPathId": 0,
    }
    yaksha_config = {
        "totalAttempts": config_instance.allowed_attempts,
        "passPercentage": config_instance.pass_percentage,
        "duration": round(config_instance.duration / 60),
        "negativeScorePercentage": int(config_instance.negative_score_percentage),
        "externalScheduleConfigArgs": f"{custom_args}",
        "assessmentConfig": {
            "enableShuffling": config_instance.is_shuffling_enabled,
            "resultType": config_instance.result_type,
            "redirectURL": "",
        },
    }
    if config_instance.is_aeye_proctoring_enabled or config_instance.is_proctoring_enabled:
        yaksha_config.update(
            {
                "enableProctoring": config_instance.is_proctoring_enabled,
                "proctoringConfig": {
                    "enableFullScreenMode": config_instance.is_full_screen_mode_enabled,
                    "restrictWindowViolation": config_instance.is_window_violation_restricted,
                    "windowViolationLimit": config_instance.window_violation_limit,
                },
                "enableAeyeProctoring": config_instance.is_aeye_proctoring_enabled,
                "aeyeProctoringConfig": config_instance.aeye_proctoring_config,
                "enablePlagiarism": config_instance.is_plagiarism_enabled,
            }
        )
    return yaksha_config


def call_yaksha_leaderboard_task(tracker, learning_type, user_id):
    """function to call leaderboard for yaksha completion"""

    if tracker.is_ccms_obj:
        extra_kwargs = {
            "is_ccms_obj": tracker.is_ccms_obj,
            "ccms_id": tracker.ccms_id,
        }
    else:
        if tracker.assessment.type == AssessmentTypeChoices.dependent_assessment:
            if learning_type == BaseLearningTypeChoices.course:
                extra_kwargs = {
                    "course_id": tracker.assessment.module.course_id,
                }
            elif learning_type == BaseLearningTypeChoices.learning_path:
                extra_kwargs = {
                    "learning_path_id": tracker.assessment.lp_course.learning_path_id,
                }
        elif tracker.assessment.type == AssessmentTypeChoices.final_assessment:
            if learning_type == BaseLearningTypeChoices.course:
                extra_kwargs = {
                    "course_id": tracker.assessment.course_id,
                }
            elif learning_type == BaseLearningTypeChoices.learning_path:
                extra_kwargs = {"learning_path_id": tracker.assessment.learning_path_id}
    CommonLeaderboardTask().run_task(
        milestone_names=MilestoneChoices.yaksha_completion,
        db_name=get_current_db_name(),
        user_id=user_id,
        **extra_kwargs,
    )


def assessment_tracker_progress_update(
    tracker,
    result_instance,
    request,
    user_id,
    learning_type=None,
):
    """updates the assessment progress."""

    max_progress_instance = result_instance.order_by("-progress").first()
    if max_progress_instance:
        tracker.available_attempt = (
            tracker.allowed_attempt + tracker.reattempt_count - result_instance.count()
            if tracker.allowed_attempt
            else 0
        )
        old_tracker_status = tracker.is_pass
        tracker.progress = max_progress_instance.progress
        tracker.is_pass = max_progress_instance.is_pass
        tracker.is_completed = True
        tracker.completion_date = timezone.now()
        tracker.save()
        if not old_tracker_status and tracker.is_pass and learning_type:
            # TODO: Need to verify if badge is exist for skill traveller or not.
            CommonBadgeTask().run_task(
                db_name=get_current_db_name(),
                category=BadgeCategoryChoices.assessment,
                learning_type=learning_type,
                tracker_id=tracker.id,
                request=request,
            )
            call_yaksha_leaderboard_task(tracker, learning_type, user_id)
    tracker.last_accessed_on = timezone.now()
    tracker.save()
    return tracker


def get_tracker_instance(user, enrollment_instance):
    """Returns the tracker instance based on enrollment instance."""

    tracker_filter_field = LEARNING_RELATED_FIELDS.get(enrollment_instance.learning_type)
    if enrollment_instance.is_ccms_obj:
        tracker_filter_field = "ccms_id"
    tracker_filter_value = getattr(enrollment_instance, tracker_filter_field)
    return (
        getattr(user, tracker_related_fields[enrollment_instance.learning_type])
        .filter(**{tracker_filter_field: tracker_filter_value})
        .first()
    )


def convert_sec_to_hms(seconds):
    """Convert seconds to 'hours:minutes:seconds' format."""

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def get_ccms_list_details(request, learning_type, params):
    """Returns the ccms learning list details."""

    headers = process_request_headers(request)
    return get_request(
        service="CCMS",
        url_path=f"api/v1/{CCMS_URL_RELATED_KEYS.get(learning_type)}/list/",
        params=params,
        headers=headers,
    )


def get_ccms_tracker_details(user, learning_type, ccms_id):
    """Returns the ccms tracker details."""

    tracker_instance = getattr(user, RELATED_TRACKER_NAMES.get(learning_type)).filter(ccms_id=ccms_id).first()
    return (
        {
            "id": tracker_instance.id,
            "progress": tracker_instance.progress,
            "completed_duration": tracker_instance.completed_duration,
            "last_accessed_on": tracker_instance.last_accessed_on,
            "completion_date": tracker_instance.completion_date,
            "is_completed": tracker_instance.is_completed,
        }
        if tracker_instance
        else None
    )


def convert_hms_to_sec(hms_string):
    """Convert 'HH:MM:SS' format to seconds."""

    try:
        hours, minutes, seconds = map(int, hms_string.split(":"))
        return hours * 3600 + minutes * 60 + seconds
    except Exception:
        return None
