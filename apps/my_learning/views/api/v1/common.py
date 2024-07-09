import requests
from django.conf import settings
from django.db.models import Q
from rest_framework.decorators import action

from apps.common.communicator import get_request, post_request
from apps.common.helpers import get_sorting_meta
from apps.common.views.api import AppModelListAPIViewSet, CatalogueFilterMixin, FavouriteFilterMixin, SortingMixin
from apps.learning.helpers import BaseLearningSkillRoleFilter
from apps.tenant_service.middlewares import get_current_tenant_details, get_current_tenant_idp_id
from apps.virtutor.helpers import convert_utc_to_ist


class BaseMyLearningSkillRoleListApiViewSet(
    SortingMixin, FavouriteFilterMixin, CatalogueFilterMixin, AppModelListAPIViewSet
):
    """Api viewset to list courses."""

    filterset_class = BaseLearningSkillRoleFilter
    search_fields = ["name", "code"]

    def sorting_options(self):
        """Returns the sorting options."""

        return self.get_default_sorting_options()

    def get_queryset(self):
        """Overridden to filter the queryset based on query params."""

        user = self.get_user()
        user_group = user.related_user_groups.all()
        if self.request.query_params.get("overall"):
            self.queryset = self.queryset.filter(
                Q(related_learning_catalogues__related_catalogue_relations__user_group__in=user_group)
                | Q(related_learning_catalogues__related_catalogue_relations__user=user)
                | Q(related_enrollments__user=user)
                | Q(related_enrollments__user_group__in=user_group)
            ).distinct()
        return self.get_sorted_queryset()

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        data["sort_by"] = get_sorting_meta(self.get_sorting_options(self.sorting_options()))
        return self.send_response(data)


def yaksha_assessment_schedule(user, assessment_id, schedule_config, idp_token, kc_flag=None):
    """Schedule the assessments in YAKSHA."""

    tenant_details = get_current_tenant_details()
    payload = {
        "tenantId": tenant_details.get("idp_id"),
        "assessmentIdNumber": assessment_id,
        "userEmailAddress": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "resultShareMode": [],
        "scheduleConfig": schedule_config,
    }
    request_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {idp_token}"}
    if kc_flag:
        yaksha_host = settings.YAKSHA_CONFIG["one_host"]
        request_headers["X-Tenant"] = tenant_details.get("tenancy_name", None)
    else:
        yaksha_host = tenant_details.get("yaksha_host", None) or settings.YAKSHA_CONFIG["host"]
    scheduled_assessment = requests.post(
        url=yaksha_host + settings.YAKSHA_CONFIG["schedule_assessment"],
        json=payload,
        headers=request_headers,
    )
    if scheduled_assessment.status_code != 200:
        return False, "Something went wrong. Contact us."
    scheduled_assessment_data = scheduled_assessment.json()
    if scheduled_assessment_data["result"]["isSuccess"]:
        return True, scheduled_assessment_data["result"]
    else:
        return False, "Something went wrong. Contact us."


def yaksha_assessment_result(user_email, assessment_id, idp_token, schedule, result_instance, kc_flag=None):
    """Returns the yaksha assessment result."""

    tenant_details = get_current_tenant_details()
    result_params = {
        "TenantId": get_current_tenant_idp_id(),
        "UserEmailAddress": user_email,
        "AssessmentIdNumber": assessment_id,
    }
    request_headers = None
    if kc_flag:
        service = "YAKSHA_ONE"
        request_headers = {"X-Tenant": tenant_details.get("tenancy_name", None)}
    else:
        service = "YAKSHA"
    success, data = get_request(
        service=service,
        url_path=settings.YAKSHA_CONFIG["get_assessment_result"],
        auth_token=idp_token,
        params=result_params,
        headers=request_headers,
    )
    if not success:
        return False, "Something went wrong. Contact us."
    if success and data["result"]["isSuccess"]:
        schedules = data["result"].get("schedules") or []
        for item in schedules:
            if item["scheduleId"] == schedule.scheduled_id:
                attempts = item["attempts"]
                for attempt in attempts:
                    # TODO: Need to give support for in_progress status
                    if attempt["status"] != "In progress":
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
                        result_instance.objects.update_or_create(
                            schedule=schedule, attempt=attempt["attemptNumber"], defaults=result_config
                        )
        return True, result_instance
    else:
        return False, data["result"]["errorMessage"]


def wecp_assessment_schedule(user_email, assessment_id):
    """Add candidates to the assessment on wecp."""

    tenant_details = get_current_tenant_details()
    if not tenant_details["is_wecp_enabled"] or not tenant_details["wecp_key"]:
        return False, "WECP not enabled or WECP key not found."
    payload = {"testId": assessment_id, "sendEmail": True, "candidates": [{"email": user_email}]}
    return post_request(
        service="WECP",
        url_path=settings.WECP_CONFIG["invite_candidates"],
        auth_token=tenant_details["wecp_key"],
        data=payload,
    )
