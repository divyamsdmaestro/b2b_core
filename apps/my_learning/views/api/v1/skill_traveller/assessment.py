from django.db.models import Q
from rest_framework.generics import get_object_or_404

from apps.common.views.api import AppAPIView, AppModelRetrieveAPIViewSet
from apps.learning.config import AssessmentTypeChoices
from apps.learning.models import STAssessment
from apps.my_learning.config import AllBaseLearningTypeChoices
from apps.my_learning.helpers import assessment_config_detail, assessment_tracker_progress_update, get_yaksha_config
from apps.my_learning.models import Enrollment, STAssessmentTracker, STAYakshaResult, STAYakshaSchedule
from apps.my_learning.serializers.v1 import (
    STATrackerListSerializer,
    STAYakshaResultListSerializer,
    STAYakshaScheduleListSerializer,
    UserSTAssessmentListSerializer,
)
from apps.my_learning.views.api.v1.common import yaksha_assessment_result, yaksha_assessment_schedule


class STAssessmentTrackerCreateApiView(AppAPIView):
    """APi view to create tracker for skill_traveller assessments."""

    def post(self, request, *args, **kwargs):
        """Create tracker for skill_traveller assessment."""

        st_assessment = get_object_or_404(STAssessment, pk=kwargs.get("st_assessment", None))
        if st_assessment.related_st_assessment_trackers.filter(user=self.get_user()).first():
            return self.send_error_response("Already started.")
        if st_assessment.type == AssessmentTypeChoices.final_assessment:
            skill_traveller = st_assessment.skill_traveller
        else:
            skill_traveller = st_assessment.st_course.skill_traveller
        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        if Enrollment.objects.filter(
            Q(user_group__in=user_groups) | Q(user=user), skill_traveller=skill_traveller, is_enrolled=True
        ).first():
            instance, created = STAssessmentTracker.objects.get_or_create(assessment=st_assessment, user=user)
            return self.send_response(STATrackerListSerializer(instance).data)
        return self.send_error_response(data="User is not enrolled for this skill_traveller.")


class STAssessmentStartApiView(AppAPIView):
    """Api view to schedule session in yaksha."""

    def post(self, request, *args, **kwargs):
        """Performs the yaksha schedule assessment."""

        user = self.get_user()
        tracker = get_object_or_404(STAssessmentTracker, pk=kwargs["tracker_pk"], user=user)
        kc_flag = False
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            kc_flag = True
        else:
            idp_token = request.headers.get("idp-token", None)
        if tracker.assessment.type == AssessmentTypeChoices.final_assessment:
            skill_traveller = tracker.assessment.skill_traveller
        else:
            skill_traveller = tracker.assessment.st_course.skill_traveller
        is_practice = tracker.assessment.is_practice
        config_instance = assessment_config_detail(
            instance_key="skill_traveller", instance=skill_traveller, is_practice=is_practice
        )
        if not config_instance:
            return self.send_error_response("Configuration not found for yaksha. Contact administrator.")
        if tracker.allowed_attempt is None and tracker.available_attempt is None:
            tracker.allowed_attempt = tracker.available_attempt = config_instance.allowed_attempts
            tracker.save()
        if schedule_instance := tracker.related_sta_yaksha_schedules.first():
            return self.send_response(STAYakshaScheduleListSerializer(schedule_instance).data)
        schedule_config = get_yaksha_config(
            config_instance=config_instance,
            learning_type=AllBaseLearningTypeChoices.skill_traveller,
            learning_id=skill_traveller.id,
            assessment_type=tracker.assessment.type,
            assessment_id=tracker.assessment.id,
            is_ccms_obj=tracker.is_ccms_obj,
        )
        success, data = yaksha_assessment_schedule(
            user=user,
            assessment_id=str(tracker.assessment.assessment_uuid),
            schedule_config=schedule_config,
            idp_token=idp_token,
            kc_flag=kc_flag,
        )
        if success:
            assessment_schedule_config = {
                "scheduled_link": data["scheduleLink"],
                "scheduled_id": data["scheduleId"],
            }
            instance, created = STAYakshaSchedule.objects.update_or_create(
                tracker=tracker,
                defaults=assessment_schedule_config,
            )
            return self.send_response(STAYakshaScheduleListSerializer(instance).data if instance else None)
        return self.send_error_response(data)


class STAYakshaResultApiView(AppAPIView):
    """Api view to return the yasksha result."""

    def post(self, request, *args, **kwargs):
        """Returns the yaksha result."""

        user = self.get_user()
        tracker = get_object_or_404(STAssessmentTracker, pk=kwargs["tracker_pk"])
        kc_flag = False
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            kc_flag = True
        else:
            idp_token = request.headers.get("idp-token", None)
        if schedule := tracker.related_sta_yaksha_schedules.first():
            yaksha_assessment_result(
                user_email=user.email,
                assessment_id=tracker.assessment.assessment_uuid,
                idp_token=idp_token,
                schedule=schedule,
                result_instance=STAYakshaResult,
                kc_flag=kc_flag,
            )
            if result_instance := schedule.related_sta_yaksha_results.order_by("attempt"):
                tracker = assessment_tracker_progress_update(
                    tracker=tracker,
                    result_instance=result_instance,
                    request={"headers": dict(request.headers)},
                    user_id=user.id,
                )
            tracker_data = STATrackerListSerializer(tracker).data
            tracker_data["results"] = STAYakshaResultListSerializer(result_instance, many=True).data
            return self.send_response(tracker_data)
        else:
            return self.send_error_response("Assessment not completed.")


class STAssessmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Retrieve api for STAssessment."""

    serializer_class = UserSTAssessmentListSerializer
    queryset = STAssessment.objects.all()
