from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import get_object_or_404

from apps.access_control.config import RoleTypeChoices
from apps.common.communicator import put_request
from apps.common.mml_communicator import mml_vm_creation
from apps.common.views.api import (
    AppAPIView,
    AppModelCreateAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    AppModelUpdateAPIViewSet,
)
from apps.learning.config import EvaluationTypeChoices, PlaygroundToolChoices
from apps.learning.helpers import AssignmentFilter, get_ccms_retrieve_details
from apps.learning.models import Assignment
from apps.my_learning.config import AllBaseLearningTypeChoices, EnrollmentTypeChoices
from apps.my_learning.helpers import (
    assignment_config_detail,
    get_ccms_list_details,
    get_ccms_tracker_details,
    get_yaksha_config,
)
from apps.my_learning.models import (
    AssignmentSubmission,
    AssignmentTracker,
    AssignmentYakshaResult,
    AssignmentYakshaSchedule,
    Enrollment,
    SubmissionFile,
)
from apps.my_learning.serializers.v1 import (
    AssignmentSubmissionCreateModelSerializer,
    AssignmentSubmissionListModelSerializer,
    AssignmentSubmissionUpdateModelSerializer,
    AssignmentYakshaResultListSerializer,
    AssignmentYakshaScheduleListSerializer,
    BaseEnrollmentListModelSerializer,
    BaseMultipleFileUploadSerializer,
    UserAssignmentListModelSerializer,
    UserAssignmentRetrieveModelSerializer,
    UserAssignmentStartSerializer,
    UserAssignmentTrackerCreateModelSerializer,
    UserAssignmentTrackerListSerializer,
)
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet
from apps.my_learning.views.api.v1.common import yaksha_assessment_result, yaksha_assessment_schedule
from apps.tenant_service.middlewares import get_current_tenant_details, get_current_tenant_idp_id


class UserAssignmentListApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """Viewset to list the assignment with enrolled_details.."""

    serializer_class = UserAssignmentListModelSerializer
    queryset = Assignment.objects.unarchived()
    filterset_class = AssignmentFilter


class UserAssignmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api view to retrieve assignments."""

    serializer_class = UserAssignmentRetrieveModelSerializer
    queryset = Assignment.objects.unarchived()


class SubmissionFileUploadApiView(AppAPIView):
    """Api view to upload the submission file."""

    serializer_class = BaseMultipleFileUploadSerializer

    def post(self, request, *args, **kwargs):
        """Handle the file upload."""

        request_headers = {"headers": dict(request.headers)}
        tracker = get_object_or_404(AssignmentTracker, pk=self.kwargs["tracker_pk"], user=self.get_user())
        serializer = self.get_valid_serializer()
        files = serializer.validated_data["file"]
        if tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment", instance_id=tracker.ccms_id, request=request_headers
            )
            if success:
                assignment_id = data["data"]["id"]
                assignment_tool = data["data"]["tool"]
                enable_submission = data["data"]["enable_submission"]
                allowed_attempts = data["data"]["allowed_attempts"]
            else:
                return self.send_error_response(data)
        else:
            assignment_id = tracker.assignment.id
            assignment_tool = tracker.assignment.tool
            enable_submission = tracker.assignment.enable_submission
            allowed_attempts = tracker.assignment.allowed_attempts
        if assignment_tool == PlaygroundToolChoices.yaksha or not enable_submission:
            return self.send_error_response({"error": "Submission not allowed."})
        submission_config = assignment_config_detail(
            assignment_id=assignment_id, enrollment=tracker.enrollment, choice=assignment_tool
        )
        if not submission_config:
            return self.send_error_response({"error": "Configuration not found. Contact administrator."})
        if tracker.allowed_attempt is None and tracker.available_attempt is None:
            tracker.allowed_attempt = tracker.available_attempt = (
                allowed_attempts or submission_config.allowed_attempts
            )
            tracker.save()
        if tracker.available_attempt == 0:
            return self.send_error_response({"error": "Max attempts reached."})
        if len(files) > submission_config.max_files_allowed:
            return self.send_error_response(
                {"files": f"Max allowed files per submission is {submission_config.max_files_allowed}"}
            )
        response = []
        for file in files:
            ext = Path(file.name).suffix[1:].lower()
            extensions_allowed = submission_config.extensions_allowed_as_list
            if ext not in extensions_allowed:
                return self.send_error_response(
                    {"files": {files.index(file): f"Allowed extensions {extensions_allowed}"}}
                )
            instance = SubmissionFile.objects.create(file=file)
            response.append({"id": instance.id, "file": instance.file_url})
        return self.send_response(response)


class AssignmentSubmissionCreateApiViewSet(AppModelCreateAPIViewSet):
    """Api view for assignment submission."""

    serializer_class = AssignmentSubmissionCreateModelSerializer
    queryset = AssignmentSubmission.objects.all()


class AssignmentSubmissionListApiViewSet(AppModelListAPIViewSet):
    """Api view to list assignment submissions."""

    serializer_class = AssignmentSubmissionListModelSerializer
    queryset = AssignmentSubmission.objects.all()
    filterset_fields = [
        "is_reviewed",
        "assignment_tracker__user",
        "assignment_tracker__is_ccms_obj",
        "assignment_tracker__user__related_user_groups",
    ]
    search_fields = [
        "assignment_tracker__user__email",
        "assignment_tracker__assignment__name",
    ]

    def get_queryset(self):
        """Overridden to return the submissions of particular tracker."""

        user = self.get_user()
        if user.current_role.role_type == RoleTypeChoices.admin or user.is_staff:
            return self.queryset
        elif user.current_role.role_type == RoleTypeChoices.author:
            return self.queryset.filter(assignment_tracker__assignment__author=user)
        else:
            tracker = get_object_or_404(AssignmentTracker, pk=self.request.query_params.get("tracker", None))
            return tracker.related_assignment_submissions.all()

    def list(self, request, *args, **kwargs):
        """Include CCMS SubModule Details."""

        response = super().list(request, *args, **kwargs)
        submissions = response.data["data"]["results"]
        ccms_obj_available, index = False, 0
        submission_ids, assignment_ids = [], []
        for submission in submissions:
            if submission["assignment"].get("is_ccms_obj"):
                ccms_obj_available = True
                assignment_ids.append(submission["assignment"]["id"])
                submission_ids.append(index)
            index += 1
        if ccms_obj_available:
            success, assignment_list = get_ccms_list_details(
                learning_type="assignment_core",
                request={"headers": request.headers},
                params={"uuid": assignment_ids},
            )
            if not success:
                return self.send_error_response(assignment_list)
            for submission_id in submission_ids:
                submission_data = submissions[submission_id]
                submission_data["assignment"] = assignment_list["data"].get(str(submission_data["assignment"]["id"]))
        return response


class AssignmentSubmissionRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api view to retrieve assignment submissions."""

    serializer_class = AssignmentSubmissionListModelSerializer
    queryset = AssignmentSubmission.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Overriden to include ccms details."""

        response = super().retrieve(request, *args, **kwargs)
        assignment_details = response.data["data"]["assignment"]
        if assignment_details.get("is_ccms_obj"):
            success, assignment_data = get_ccms_retrieve_details(
                learning_type="assignment",
                instance_id=str(assignment_details["id"]),
                request={"headers": request.headers},
            )
            if not success:
                return self.send_error_response(assignment_data)
            response.data["data"]["assignment"] = assignment_data["data"]
        return response


class AssignmentSubmissionUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api view to update assignment submission."""

    serializer_class = AssignmentSubmissionUpdateModelSerializer
    queryset = AssignmentSubmission.objects.all()


class UserAssignmentTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """View for assignment tracker cud."""

    serializer_class = UserAssignmentTrackerCreateModelSerializer
    queryset = AssignmentTracker.objects.all()


class UserAssignmentTrackerListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the assignment trackers."""

    serializer_class = UserAssignmentTrackerListSerializer
    queryset = AssignmentTracker.objects.all()
    filterset_fields = ["user"]
    search_fields = ["user__email", "assignment__name"]

    def get_queryset(self):
        """Returns the assignment tracker based on assignment."""

        assignment = get_object_or_404(Assignment, pk=self.kwargs["assignment_pk"])
        return assignment.related_assignment_trackers.all()


class UserAssignmentStartApiView(AppAPIView):
    """Api view to perform yaksha or mml operations."""

    serializer_class = UserAssignmentStartSerializer

    def post(self, request, *args, **kwargs):
        """Performs the yaksha schedule assessment or mml vm_creation."""

        request_headers = {"headers": dict(request.headers)}
        validated_data = self.get_valid_serializer().validated_data

        # Extra condition for KC
        kc_flag = False
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            kc_flag = True
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")

        tracker = validated_data["tracker"]
        user = self.get_user()
        if tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment", instance_id=tracker.ccms_id, request=request_headers
            )
            if success:
                assignment_id = data["data"]["id"]
                assignment_tool = data["data"]["tool"]
                mml_sku_id = data["data"]["mml_sku_id"]
                vm_name = data["data"]["vm_name"]
                yaksha_uuid = data["data"]["assessment_uuid"]
                allowed_attempts = data["data"]["allowed_attempts"]
            else:
                return self.send_error_response(data)
        else:
            learning_type = validated_data["learning_type"]
            learning_instance = validated_data[learning_type]
            assignment_id = tracker.assignment.id
            assignment_tool = tracker.assignment.tool
            mml_sku_id = getattr(learning_instance, "mml_sku_id", None)
            vm_name = getattr(learning_instance, "vm_name", None)
            yaksha_uuid = tracker.assignment.assessment_uuid
            allowed_attempts = tracker.assignment.allowed_attempts
        assignment_config = assignment_config_detail(
            assignment_id=assignment_id, enrollment=tracker.enrollment, choice=assignment_tool
        )
        if not assignment_config:
            return self.send_error_response(f"Configuration not found for {assignment_tool}. Contact administrator.")
        if tracker.allowed_attempt is None and tracker.available_attempt is None:
            tracker.allowed_attempt = tracker.available_attempt = (
                allowed_attempts or assignment_config.allowed_attempts
            )
            tracker.save()
        if assignment_tool == PlaygroundToolChoices.yaksha:
            if schedule_instance := tracker.related_assignment_yaksha_schedules.first():
                return self.send_response(AssignmentYakshaScheduleListSerializer(schedule_instance).data)
            schedule_config = get_yaksha_config(
                config_instance=assignment_config,
                learning_type=AllBaseLearningTypeChoices.assignment,
                learning_id=assignment_id,
                assessment_type=None,
                assessment_id=None,
                is_ccms_obj=tracker.is_ccms_obj,
            )
            if allowed_attempts:
                schedule_config.update({"totalAttempts": allowed_attempts})
            success, data = yaksha_assessment_schedule(
                user=user,
                assessment_id=str(yaksha_uuid),
                schedule_config=schedule_config,
                idp_token=idp_token,
                kc_flag=kc_flag,
            )
            if success:
                assessment_schedule_config = {
                    "scheduled_link": data["scheduleLink"],
                    "scheduled_id": data["scheduleId"],
                }
                instance, created = AssignmentYakshaSchedule.objects.update_or_create(
                    assignment_tracker=tracker,
                    defaults=assessment_schedule_config,
                )
                return self.send_response(AssignmentYakshaScheduleListSerializer(instance).data if instance else None)
            return self.send_error_response(data)
        elif assignment_tool == PlaygroundToolChoices.mml:
            success, data, headers = mml_vm_creation(
                idp_token=idp_token, vm_name=vm_name, mml_sku_id=str(mml_sku_id), kc_flag=kc_flag
            )
            if success:
                data["headers"] = headers
                return self.send_response(data)
            else:
                return self.send_error_response(data)
        return self.send_response()


class UserAssignmentResultApiView(AppAPIView):
    """Api view to return the assignment result."""

    def update_tracker_progress(self, instances, tracker, evaluation_type):
        """Update the tracker progress."""

        max_progress_instance = instances.order_by("-progress").first()
        tracker.progress = max_progress_instance.progress if max_progress_instance else 0
        tracker.available_attempt = tracker.allowed_attempt - instances.count()
        tracker.is_pass = max_progress_instance.is_pass if max_progress_instance else None
        if evaluation_type == EvaluationTypeChoices.non_evaluated:
            tracker.progress = 100
            tracker.is_completed = True
            tracker.completion_date = timezone.now()
        elif evaluation_type == EvaluationTypeChoices.evaluated and max_progress_instance.is_pass:
            tracker.progress = 100
            tracker.is_completed = True
            tracker.completion_date = timezone.now()
        else:
            tracker.is_completed = False
        tracker.last_accessed_on = timezone.now()
        tracker.save()
        return tracker

    def get_yaksha_result(self, user, tracker, idp_token, schedule, yaksha_uuid, evaluation_type, kc_flag=None):
        """Perform the yaksha assessment result and returns the updated assignment result."""

        if tracker.available_attempt > 0:
            success, data = yaksha_assessment_result(
                user_email=user.email,
                assessment_id=yaksha_uuid,
                idp_token=idp_token,
                schedule=schedule,
                result_instance=AssignmentYakshaResult,
                kc_flag=kc_flag,
            )
            if not success:
                return self.send_error_response(data)
            if result_instance := schedule.related_assignment_yaksha_results.order_by("attempt"):
                tracker = self.update_tracker_progress(
                    instances=result_instance, tracker=tracker, evaluation_type=evaluation_type
                )
        result_instance = schedule.related_assignment_yaksha_results.order_by("attempt")
        return tracker, AssignmentYakshaResultListSerializer(result_instance, many=True).data

    def post(self, request, *args, **kwargs):
        """Returns the assignment result."""

        user = self.get_user()
        request_headers = {"headers": dict(request.headers)}
        tracker = get_object_or_404(AssignmentTracker, pk=self.kwargs["tracker_pk"], user=user)
        kc_flag = False
        if "kc-token" in request.headers:
            kc_flag = True
            idp_token = request.headers.get("kc-token", None)
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        yaksha_results, data = None, {}
        if tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment", instance_id=tracker.ccms_id, request=request_headers
            )
            if success:
                assignment_tool = data["data"]["tool"]
                yaksha_uuid = data["data"]["assessment_uuid"]
                evaluation_type = data["data"]["evaluation_type"]
            else:
                return self.send_error_response(data)
        else:
            assignment_tool = tracker.assignment.tool
            yaksha_uuid = tracker.assignment.assessment_uuid
            evaluation_type = tracker.assignment.evaluation_type
        if assignment_tool == PlaygroundToolChoices.yaksha:
            if schedule := tracker.related_assignment_yaksha_schedules.first():
                tracker, yaksha_results = self.get_yaksha_result(
                    user, tracker, idp_token, schedule, yaksha_uuid, evaluation_type, kc_flag=kc_flag
                )
            else:
                return self.send_error_response("Assignment not completed.")
        if submissions := tracker.related_assignment_submissions.filter(is_reviewed=True):
            if tracker.available_attempt > 0:
                tracker = self.update_tracker_progress(
                    instances=submissions, tracker=tracker, evaluation_type=evaluation_type
                )
        if not tracker.is_ccms_obj:
            tracker.assignment_relation_progress_update()
        submission_results = AssignmentSubmissionListModelSerializer(
            tracker.related_assignment_submissions.all(), many=True, context={"assignment": data.get("data")}
        ).data
        tracker_data = UserAssignmentTrackerListSerializer(tracker).data
        tracker_data["yaksha_results"] = yaksha_results
        tracker_data["submission_results"] = submission_results
        return self.send_response(tracker_data)


class AssignmentReattemptApiView(AppAPIView):
    """Api view to enable the reattempt of an assignment."""

    def post(self, request, *args, **kwargs):
        """Performs the reattempt operation."""

        tracker = get_object_or_404(AssignmentTracker, pk=self.kwargs["tracker_pk"])
        tenant_details = get_current_tenant_details()
        request_headers = None
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            service = "YAKSHA_ONE"
            request_headers = {"X-Tenant": tenant_details.get("tenancy_name", None)}
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
            service = "YAKSHA"
        if tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                learning_type="assignment", instance_id=tracker.ccms_id, request={"headers": dict(request.headers)}
            )
            if success:
                tool = data["data"]["tool"]
            else:
                return self.send_error_response(data)
        else:
            tool = tracker.assignment.tool
        if tracker.available_attempt > 0:
            return self.send_error_response("Reattempt not allowed.")
        if tool == PlaygroundToolChoices.yaksha:
            if schedule := tracker.related_assignment_yaksha_schedules.first():
                update_config = {
                    "tenantId": get_current_tenant_idp_id(),
                    "userEmail": tracker.user.email,
                    "scheduleId": schedule.scheduled_id,
                    "updateAttemptCountBy": 1,
                }
                success, data = put_request(
                    service=service,
                    url_path=settings.YAKSHA_CONFIG["update_user_attempt"],
                    auth_token=idp_token,
                    data=update_config,
                    headers=request_headers,
                )
                if not success:
                    return self.send_error_response("Something went wrong. Contact us")
            else:
                return self.send_error_response("Yaksha Schedule Not Found.")
        tracker.available_attempt = 1
        tracker.allowed_attempt += 1
        tracker.save()
        return self.send_response("Success")


class UserCCMSAssignmentRetrieveApiView(AppAPIView):
    """Assignment retrieve from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS assignment with enrollment details."""

        from apps.learning.helpers import get_ccms_retrieve_details

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        assignment_id = kwargs.get("uuid")
        success, data = get_ccms_retrieve_details(
            learning_type=EnrollmentTypeChoices.assignment,
            instance_id=assignment_id,
            request=request_headers,
            params=request_params,
        )
        if not success:
            return self.send_error_response(data["data"])
        result = data["data"]
        if result:
            result = self.process_assignment_tracker(result)
        return self.send_response(result)

    def process_assignment_tracker(self, result):
        """Process the assignment tracker & enrollment for a given result."""

        assignment_id = result["uuid"]
        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        enrollment_instance = Enrollment.objects.filter(
            Q(user_group__in=user_groups) | Q(user=user),
            learning_type=EnrollmentTypeChoices.assignment,
            ccms_id=assignment_id,
        ).first()
        result["enrolled_details"] = (
            BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
            if enrollment_instance
            else None
        )
        result["tracker_detail"] = get_ccms_tracker_details(
            user=user, learning_type=EnrollmentTypeChoices.assignment, ccms_id=assignment_id
        )
        return result
