from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppAPIView, AppModelCreateAPIViewSet, AppModelRetrieveAPIViewSet
from apps.leaderboard.config import BadgeLearningTypeChoices
from apps.learning.config import AssessmentProviderTypeChoices, AssessmentTypeChoices
from apps.learning.helpers import get_ccms_retrieve_details
from apps.learning.models import LPAssessment
from apps.my_learning.config import AllBaseLearningTypeChoices
from apps.my_learning.helpers import assessment_config_detail, assessment_tracker_progress_update, get_yaksha_config
from apps.my_learning.models import LPAssessmentTracker, LPAYakshaResult, LPAYakshaSchedule
from apps.my_learning.serializers.v1 import (
    LPATrackerCreateSerializer,
    LPATrackerListSerializer,
    LPAYakshaResultListSerializer,
    LPAYakshaScheduleListSerializer,
    UserLPAssessmentListSerializer,
)
from apps.my_learning.views.api.v1.common import (
    wecp_assessment_schedule,
    yaksha_assessment_result,
    yaksha_assessment_schedule,
)


class LPAssessmentTrackerCreateAPiViewSet(AppModelCreateAPIViewSet):
    """APi view to create tracker for learning_path assessments."""

    serializer_class = LPATrackerCreateSerializer
    queryset = LPAssessmentTracker.objects.all()


class LPAssessmentStartApiView(AppAPIView):
    """Api view to schedule session in yaksha."""

    def post(self, request, *args, **kwargs):
        """Performs the yaksha schedule assessment."""

        user = self.get_user()
        tracker = get_object_or_404(LPAssessmentTracker, pk=kwargs["tracker_pk"], user=user)
        kc_flag = False
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            kc_flag = True
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        if schedule_instance := tracker.related_lpa_yaksha_schedules.first():
            return self.send_response(LPAYakshaScheduleListSerializer(schedule_instance).data)
        success, schedule_id, wecp_invite_id, schedule_link = self.schedule_assessment(
            tracker, user, idp_token, kc_flag=kc_flag
        )
        if not success:
            return self.send_error_response(schedule_id)
        schedule_id = schedule_id
        schedule_link = schedule_link
        wecp_invite_id = wecp_invite_id
        assessment_schedule_config = {
            "scheduled_link": schedule_link,
            "scheduled_id": schedule_id,
            "wecp_invite_id": wecp_invite_id,
        }
        instance, created = LPAYakshaSchedule.objects.update_or_create(
            tracker=tracker,
            defaults=assessment_schedule_config,
        )
        return self.send_response(LPAYakshaScheduleListSerializer(instance).data if instance else None)

    def schedule_assessment(self, tracker, user, token, kc_flag=None):
        """Returns the assessment scheduled details."""

        request_headers = {"headers": dict(self.request.headers)}
        if not tracker.is_ccms_obj:
            is_practice = tracker.assessment.is_practice
            assessment_uuid = tracker.assessment.assessment_uuid
            assessment_id = tracker.assessment.id
            assessment_type = tracker.assessment.type
            if assessment_type == AssessmentTypeChoices.final_assessment:
                learning_path = tracker.assessment.learning_path
            else:
                learning_path = tracker.assessment.lp_course.learning_path
            learning_id = learning_path.id
            if tracker.assessment.provider_type == AssessmentProviderTypeChoices.wecp:
                success, data = wecp_assessment_schedule(user_email=user.email, assessment_id=str(assessment_uuid))
                if not success:
                    return False, data, None, None
                schedule_id = 0
                wecp_invite_id = data[0]["_id"] if success and len(data) > 0 else None
                schedule_link = data[0]["link"] if success and len(data) > 0 else None
                return True, schedule_id, wecp_invite_id, schedule_link
        else:
            success, data = get_ccms_retrieve_details(
                learning_type="lp_assessment", instance_id=tracker.ccms_id, request=request_headers, params=None
            )
            if not success:
                return False, data["data"], None, None
            assessment_uuid = data["data"]["assessment_uuid"]
            assessment_id = data["data"]["id"]
            assessment_type = data["data"]["type"]
            if assessment_type == AssessmentTypeChoices.final_assessment:
                learning_id = data["data"]["learning_path"]["uuid"]
            else:
                learning_id = data["data"]["lp_course"]["learning_path"]["uuid"]
            is_practice = data["data"]["is_practice"]
            learning_path = None
        config_instance = assessment_config_detail(
            instance_key="learning_path",
            instance=learning_path,
            is_practice=is_practice,
            is_ccms_obj=tracker.is_ccms_obj,
        )
        if not config_instance:
            return False, "Configuration not found for yaksha. Contact administrator.", None, None
        if tracker.allowed_attempt is None and tracker.available_attempt is None:
            tracker.allowed_attempt = tracker.available_attempt = config_instance.allowed_attempts
            tracker.save()
        schedule_config = get_yaksha_config(
            config_instance=config_instance,
            learning_type=AllBaseLearningTypeChoices.learning_path,
            learning_id=learning_id,
            assessment_type=assessment_type,
            assessment_id=assessment_id,
            is_ccms_obj=tracker.is_ccms_obj,
        )
        success, data = yaksha_assessment_schedule(
            user=user,
            assessment_id=str(assessment_uuid),
            schedule_config=schedule_config,
            idp_token=token,
            kc_flag=kc_flag,
        )
        if not success:
            return success, data, None, None
        schedule_id = data["scheduleId"]
        schedule_link = data["scheduleLink"]
        wecp_invite_id = None
        return True, schedule_id, wecp_invite_id, schedule_link


class LPAYakshaResultApiView(AppAPIView):
    """Api view to return the yasksha result."""

    def post(self, request, *args, **kwargs):
        """Returns the yaksha result."""

        user = self.get_user()
        tracker = get_object_or_404(LPAssessmentTracker, pk=kwargs["tracker_pk"])
        kc_flag = False
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            kc_flag = True
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        request_headers = {"headers": dict(request.headers)}
        if tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="lp_assessment", instance_id=tracker.ccms_id, request=request_headers, params=None
            )
            if not success:
                return self.send_error_response(data["data"])
            yaksha_id = data["data"]["assessment_uuid"]
            provider_type = data["data"]["provider_type"]
        else:
            yaksha_id = tracker.assessment.assessment_uuid
            provider_type = tracker.assessment.provider_type
        if schedule := tracker.related_lpa_yaksha_schedules.first():
            if provider_type != AssessmentProviderTypeChoices.wecp:
                yaksha_assessment_result(
                    user_email=user.email,
                    assessment_id=tracker.assessment_uuid or yaksha_id,
                    idp_token=idp_token,
                    schedule=schedule,
                    result_instance=LPAYakshaResult,
                    kc_flag=kc_flag,
                )
            if result_instance := schedule.related_lpa_yaksha_results.order_by("attempt"):
                tracker = assessment_tracker_progress_update(
                    tracker=tracker,
                    result_instance=result_instance,
                    learning_type=BadgeLearningTypeChoices.learning_path,
                    request={"headers": dict(request.headers)},
                    user_id=user.id,
                )
            tracker_data = LPATrackerListSerializer(tracker).data
            tracker_data["results"] = LPAYakshaResultListSerializer(result_instance, many=True).data
            return self.send_response(tracker_data)
        else:
            return self.send_error_response("Assessment not completed.")


class LPAssessmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Retrieve api for LPAssessment."""

    serializer_class = UserLPAssessmentListSerializer
    queryset = LPAssessment.objects.all()


class CCMSLPAssessmentRetrieveApiView(AppAPIView):
    """Retrieve api view for ccms lp-assessments."""

    def get(self, request, *args, **kwargs):
        """Returns the ccms lp-assessment with tracker details."""

        from apps.learning.helpers import get_ccms_retrieve_details

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        lpa_id = kwargs.get("uuid")
        success, data = get_ccms_retrieve_details(
            learning_type="lp_assessment",
            instance_id=lpa_id,
            request=request_headers,
            params=request_params,
        )
        if not success:
            return self.send_error_response(data["data"])
        result = data["data"]
        if result:
            result = self.process_assessment_tracker(result)
        return self.send_response(result)

    def process_assessment_tracker(self, result):
        """Process the assessment tracker."""

        user = self.get_user()
        assessment_uuid = result["uuid"]
        assessment_tracker = user.related_lp_assessment_trackers.filter(
            is_ccms_obj=True, ccms_id=assessment_uuid
        ).first()
        result["tracker_detail"] = LPATrackerListSerializer(assessment_tracker).data if assessment_tracker else None
        return result
