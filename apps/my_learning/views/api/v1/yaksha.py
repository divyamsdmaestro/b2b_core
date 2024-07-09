from django.conf import settings
from django.db.models import Q
from rest_framework import serializers

from apps.access.models import User
from apps.common.communicator import put_request
from apps.common.serializers import AppSerializer
from apps.common.views.api import AppAPIView
from apps.learning.config import AssessmentProviderTypeChoices
from apps.learning.helpers import get_ccms_retrieve_details
from apps.my_learning.config import AllBaseLearningTypeChoices
from apps.my_learning.models import CourseAssessmentTracker, LPAssessmentTracker, STAssessmentTracker
from apps.my_learning.serializers.v1 import CATrackerListSerializer, LPATrackerListSerializer, STATrackerListSerializer
from apps.tenant_service.middlewares import get_current_tenant_details, get_current_tenant_idp_id

assessment_tracker_models = {
    AllBaseLearningTypeChoices.course: CourseAssessmentTracker,
    AllBaseLearningTypeChoices.learning_path: LPAssessmentTracker,
    AllBaseLearningTypeChoices.skill_traveller: STAssessmentTracker,
}

assessment_tracker_list_serializer = {
    AllBaseLearningTypeChoices.course: CATrackerListSerializer,
    AllBaseLearningTypeChoices.learning_path: LPATrackerListSerializer,
    AllBaseLearningTypeChoices.skill_traveller: STATrackerListSerializer,
}

yaksha_schedule_model = {
    AllBaseLearningTypeChoices.course: "related_ca_yaksha_schedules",
    AllBaseLearningTypeChoices.learning_path: "related_lpa_yaksha_schedules",
    AllBaseLearningTypeChoices.skill_traveller: "related_sta_yaksha_schedules",
}


class YakshaAssessmentTrackerListApiView(AppAPIView):
    """Returns the assessment tracker for the user."""

    def get(self, request, *args, **kwargs):
        """Returns the assessment tracker based on request."""

        learning_type = self.request.query_params.get("learning_type")
        assessment_id = self.request.query_params.get("assessment_id")
        user_id = self.request.query_params.get("user")
        # Get the related models & serializers based on learning_type
        assessment_tracker_model = assessment_tracker_models.get(learning_type)
        serializer = assessment_tracker_list_serializer.get(learning_type)
        tracker = None
        if learning_type and assessment_id and user_id and assessment_tracker_model:
            trackers = assessment_tracker_model.objects.filter(assessment_id=assessment_id)
            match learning_type:
                case AllBaseLearningTypeChoices.course:
                    tracker = trackers.filter(
                        Q(course_tracker__user_id=user_id) | Q(module_tracker__course_tracker__user_id=user_id),
                        related_ca_yaksha_schedules__isnull=False,
                    ).first()
                case AllBaseLearningTypeChoices.learning_path:
                    tracker = trackers.filter(related_lpa_yaksha_schedules__isnull=False, user_id=user_id).first()
                case AllBaseLearningTypeChoices.skill_traveller:
                    tracker = trackers.filter(related_sta_yaksha_schedules__isnull=False, user_id=user_id).first()
        return self.send_response(serializer(tracker).data if tracker else None)


class YakshaAttemptUpdateApiView(AppAPIView):
    """Update attempts for yaksha assessment."""

    class _Serializer(AppSerializer):
        """Serializer class to update yaksha assessment."""

        learning_type = serializers.ChoiceField(choices=AllBaseLearningTypeChoices.choices)
        tracker_id = serializers.IntegerField(required=True)
        attempt = serializers.IntegerField(required=True)
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.active(), required=True)

        def validate(self, attrs):
            """Validate the tracker_id is present or not."""

            tracker_model = assessment_tracker_models.get(attrs["learning_type"])
            if not tracker_model:
                raise serializers.ValidationError({"learning_type": "Assessment not present for this learning_type."})
            tracker = tracker_model.objects.filter(id=attrs["tracker_id"]).first()
            if not tracker:
                raise serializers.ValidationError({"tracker_id": "Invalid details provided."})
            if tracker.is_ccms_obj:
                success, data = get_ccms_retrieve_details(
                    learning_type="course_assessment",
                    instance_id=tracker.ccms_id,
                    request={"headers": dict(self.context["request"].headers)},
                )
                if not success:
                    raise serializers.ValidationError({"ccms_id": data["data"]})
                provider_type = data["data"]["provider_type"]
            else:
                provider_type = getattr(tracker.assessment, "provider_type", None)
            if provider_type == AssessmentProviderTypeChoices.wecp:
                raise serializers.ValidationError({"tracker_id": "Assessment type must be yaksha."})
            if tracker.available_attempt > 0:
                raise serializers.ValidationError({"tracker_id": "Attempt update not allowed."})
            self.context["tracker"] = tracker
            return attrs

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Updating yaksha asssessments."""

        serializer = self.get_valid_serializer()
        validated_data = serializer.validated_data
        request_headers = None
        tenant_details = get_current_tenant_details()
        if "kc-token" in request.headers:
            token = self.request.headers.get("kc-token", None)
            service = "YAKSHA_ONE"
            request_headers = {"X-Tenant": tenant_details.get("tenancy_name", None)}
        else:
            token = self.request.headers.get("idp-token", None) or self.request.headers.get("sso-token", None)
            service = "YAKSHA"
        tracker = serializer.context["tracker"]
        learning_type = validated_data["learning_type"]
        attempt = validated_data["attempt"]
        user = validated_data["user"]
        schedule_field = yaksha_schedule_model.get(learning_type)
        if schedule := getattr(tracker, schedule_field).first():
            update_config = {
                "tenantId": get_current_tenant_idp_id(),
                "userEmail": user.email,
                "scheduleId": schedule.scheduled_id,
                "updateAttemptCountBy": attempt,
            }
            success, data = put_request(
                service=service,
                url_path=settings.YAKSHA_CONFIG["update_user_attempt"],
                auth_token=token,
                data=update_config,
                headers=request_headers,
            )
            if success:
                tracker.reattempt_count += attempt
                tracker.available_attempt += attempt
                tracker.save()
                return self.send_response("Success")
            else:
                return self.send_error_response(data)
        else:
            return self.send_error_response("Assessment not scheduled for this user.")
