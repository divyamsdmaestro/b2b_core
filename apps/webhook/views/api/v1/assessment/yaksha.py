import json

from django.core.exceptions import ObjectDoesNotExist

from apps.access.models import User
from apps.common.idp_service import idp_admin_auth_token
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.learning.config import AssessmentTypeChoices
from apps.my_learning.config import AllBaseLearningTypeChoices
from apps.my_learning.helpers import assessment_tracker_progress_update
from apps.my_learning.models import CAYakshaSchedule, LPAYakshaSchedule
from apps.tenant.models import Tenant
from apps.virtutor.helpers import convert_utc_to_ist

yaksha_schedule_related_models = {
    AllBaseLearningTypeChoices.course: CAYakshaSchedule,
    AllBaseLearningTypeChoices.learning_path: LPAYakshaSchedule,
}

yaksha_result_related_models = {
    AllBaseLearningTypeChoices.course: "related_ca_yaksha_results",
    AllBaseLearningTypeChoices.learning_path: "related_lpa_yaksha_results",
}


class YakshaResultWebhookAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """YAKSHA webhook api view to store the yaksha results to corresponding tenant users."""

    def post(self, request, *args, **kwargs):
        """Store the yaksha results."""

        assessment_data = request.data
        user_email = assessment_data.get("userEmailAddress", None)
        schedules = assessment_data.get("schedules", [])
        for schedule in schedules:
            attempts = schedule.get("attempts", [])
            schedule_id = schedule.get("scheduleId", None)
            if schedule_config := schedule.get("externalScheduleConfigArgs", None):
                schedule_config = json.loads(schedule_config.replace("'", '"'))
                learning_type = schedule_config.get("learning_type", None)
                assessment_type = schedule_config.get("assessment_type", None)
                try:
                    tt = Tenant.objects.get(idp_id=schedule_config["tenant_id"])
                except:  # noqa
                    return self.send_error_response("Tenant detail ot found")
                tt.activate_db()
                user_related_field = "tracker__user__email"
                if learning_type == AllBaseLearningTypeChoices.course:
                    if assessment_type == AssessmentTypeChoices.final_assessment:
                        user_related_field = "tracker__course_tracker__user__email"
                    elif assessment_type == AssessmentTypeChoices.dependent_assessment:
                        user_related_field = "tracker__module_tracker__course_tracker__user__email"
                if yaksha_schedule_model := yaksha_schedule_related_models.get(learning_type, None):
                    if schedule_instance := yaksha_schedule_model.objects.filter(
                        scheduled_id=schedule_id, **{user_related_field: user_email}
                    ).first():
                        for attempt in attempts:
                            start_time = convert_utc_to_ist(attempt["actualStart"])
                            end_time = convert_utc_to_ist(attempt["actualEnd"])
                            result_config = {
                                "duration": attempt["duration"] * 60,
                                "total_questions": attempt["totalQuestions"],
                                "answered": attempt["answeredQuestions"],
                                "progress": attempt["scorePercentage"],
                                "start_time": start_time,
                                "end_time": end_time,
                                "is_pass": attempt["status"] == "Passed",
                            }
                            getattr(
                                schedule_instance, yaksha_result_related_models.get(learning_type)
                            ).update_or_create(attempt=attempt["attemptNumber"], defaults=result_config)
                        if result_instance := getattr(
                            schedule_instance, yaksha_result_related_models.get(learning_type)
                        ).order_by("attempt"):
                            auth_token = idp_admin_auth_token(raise_drf_error=True, field="name")
                            request_headers = {"headers": {"Idp-Token": auth_token}}
                            try:
                                user_id = User.objects.get(email=user_email)
                            except ObjectDoesNotExist:
                                user_id = None
                            assessment_tracker_progress_update(
                                tracker=schedule_instance.tracker,
                                result_instance=result_instance,
                                learning_type=learning_type,
                                request=request_headers,
                                user_id=user_id,
                            )
                else:
                    return self.send_error_response("Learning type not supported.")
                tt.deactivate_db()
        return self.send_response("Success")
