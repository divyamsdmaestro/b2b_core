from pathlib import Path

from rest_framework.generics import get_object_or_404

from apps.access_control.config import RoleTypeChoices
from apps.common.pagination import TempPagination
from apps.common.views.api import (
    AppAPIView,
    AppModelCreateAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    AppModelUpdateAPIViewSet,
)
from apps.learning.config import SubModuleTypeChoices
from apps.learning.helpers import get_ccms_retrieve_details
from apps.learning.models import CourseSubModule
from apps.meta.models import MMLConfiguration
from apps.my_learning.helpers import get_ccms_list_details
from apps.my_learning.models import (
    CourseModuleTracker,
    CourseSubModuleTracker,
    SubmissionFile,
    SubModuleFileSubmission,
)
from apps.my_learning.serializers.v1 import (
    BaseMultipleFileUploadSerializer,
    CourseSubModuleTrackerCreateSerializer,
    CourseSubModuleTrackerListSerializer,
    CourseSubModuleTrackerRetrieveSerializer,
    CourseSubModuleTrackerUpdateSerializer,
    SubModuleFileSubmissionCreateSerializer,
    SubModuleFileSubmissionListSerializer,
    SubModuleFileSubmissionUpdateSerializer,
    UserCourseSubModuleListSerializer,
)


class UserCourseSubModuleListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the course sub_modules."""

    serializer_class = UserCourseSubModuleListSerializer
    pagination_class = TempPagination

    def get_queryset(self):
        """Returns the course sub_module trackers."""

        tracker_pk = self.kwargs.get("tracker_pk")
        tracker_instance = get_object_or_404(CourseModuleTracker, pk=tracker_pk)
        return (
            CourseSubModule.objects.alive().filter(module=tracker_instance.module).order_by("sequence", "created_at")
        )


class SubModuleTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """Api view to create a sub modules."""

    serializer_class = CourseSubModuleTrackerCreateSerializer
    queryset = CourseSubModuleTracker.objects.all()


class SubModuleTrackerUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api View to update the progress of the course based on modules & sub_modules."""

    serializer_class = CourseSubModuleTrackerUpdateSerializer
    queryset = CourseSubModuleTracker.objects.all()

    # def update(self, request, *args, **kwargs):
    #     """Overridden to validate the module is locked."""
    #
    #     self.get_object()
    #     # if instance.module_tracker.is_locked:
    #     #     return self.send_error_response("Module is locked.")
    #     return super().update(request, *args, **kwargs)


class SubModuleTrackerRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Submodule retrieve api view set."""

    serializer_class = CourseSubModuleTrackerRetrieveSerializer
    queryset = CourseSubModuleTracker.objects.all()


class UserCCMSCourseSubModuleListApiView(AppAPIView):
    """Course submodule list api view from ccms with tracker details."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS course modules with tracker details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        tracker_pk = self.kwargs.get("tracker_pk")
        tracker_instance = get_object_or_404(CourseModuleTracker, pk=tracker_pk, course_tracker__user=self.get_user())
        if not tracker_instance.is_ccms_obj:
            return self.send_error_response("Detail not found")
        request_params.update({"module__uuid": tracker_instance.ccms_id})
        success, data = get_ccms_list_details(
            request=request_headers, learning_type="course_submodule", params=request_params
        )
        if success:
            results = data["data"]["results"]
            for result in results:
                submodule_uuid = result["uuid"]
                submodule_tracker = tracker_instance.related_course_sub_module_trackers.filter(
                    is_ccms_obj=True, ccms_id=submodule_uuid
                ).first()
                result["tracker_details"] = (
                    CourseSubModuleTrackerListSerializer(submodule_tracker, context=self.get_serializer_context()).data
                    if submodule_tracker
                    else None
                )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])


class SubModuleFileUploadApiView(AppAPIView):
    """Api view to upload the submission file."""

    serializer_class = BaseMultipleFileUploadSerializer

    def post(self, request, *args, **kwargs):
        """Handle the file upload."""

        tracker = get_object_or_404(CourseSubModuleTracker, pk=self.kwargs["tracker_pk"])
        request_headers = {"headers": dict(request.headers)}
        if tracker.is_ccms_obj:
            success, data = get_ccms_retrieve_details(
                request=request_headers, learning_type="course_submodule", instance_id=str(tracker.ccms_id)
            )
            if success:
                submodule_type = data["data"]["type"]["id"]
                course = None
            else:
                return self.send_error_response(data["data"])
        else:
            submodule_type = tracker.sub_module.type
            course = tracker.sub_module.module.course
        if submodule_type != SubModuleTypeChoices.file_submission:
            return self.send_error_response(
                {"sub_module_tracker": f"file submission is not allowed for this {submodule_type}"}
            )
        if tracker.module_tracker.course_tracker.user != self.get_user():
            return self.send_error_response({"sub_module_tracker": "Invalid Tracker"})
        validated_data = self.get_valid_serializer().validated_data
        files = validated_data["file"]
        submission_config = (
            MMLConfiguration.objects.filter(course=course, course__isnull=False)
            or MMLConfiguration.objects.filter(is_default=True)
        ).first()
        if not submission_config:
            return self.send_error_response({"error": "Configuration not found. Contact administrator."})
        if tracker.available_attempt is None:
            tracker.available_attempt = submission_config.allowed_attempts
            tracker.save()
        if tracker.available_attempt == 0:
            return self.send_error_response({"error": "Max attempts reached"})
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


class SubModuleFileSubmissionCreateApiViewSet(AppModelCreateAPIViewSet):
    """Api view for sub module file submission."""

    serializer_class = SubModuleFileSubmissionCreateSerializer
    queryset = SubModuleFileSubmission.objects.all()


class SubModuleFileSubmissionListApiViewSet(AppModelListAPIViewSet):
    """Api view to list submodule file submissions."""

    serializer_class = SubModuleFileSubmissionListSerializer
    queryset = SubModuleFileSubmission.objects.all()
    filterset_fields = [
        "is_reviewed",
        "sub_module_tracker__module_tracker__course_tracker__user",
        "sub_module_tracker__module_tracker__course_tracker__user__related_user_groups",
        "sub_module_tracker__is_ccms_obj",
    ]
    search_fields = [
        "sub_module_tracker__sub_module__name",
        "sub_module_tracker__module_tracker__course_tracker__user__email",
        "sub_module_tracker__module_tracker__course_tracker__course__name",
    ]

    def get_queryset(self):
        """Overridden to return the submissions of particular tracker."""

        user = self.get_user()
        if user.current_role.role_type == RoleTypeChoices.admin or user.is_staff:
            return self.queryset
        elif user.current_role.role_type == RoleTypeChoices.author:
            return self.queryset.filter(sub_module_tracker__sub_module__author=user)
        else:
            tracker = get_object_or_404(CourseSubModuleTracker, pk=self.request.query_params.get("tracker", None))
            return tracker.related_sub_module_submissions.all()

    def list(self, request, *args, **kwargs):
        """Include CCMS SubModule Details."""

        response = super().list(request, *args, **kwargs)
        submissions = response.data["data"]["results"]
        ccms_obj_available, index = False, 0
        submission_ids, submodule_ids = [], []
        for submission in submissions:
            if submission["sub_module"].get("is_ccms_obj"):
                ccms_obj_available = True
                submodule_ids.append(submission["sub_module"]["id"])
                submission_ids.append(index)
            index += 1
        if ccms_obj_available:
            success, sub_module_list = get_ccms_list_details(
                learning_type="core_submodule",
                request={"headers": request.headers},
                params={"uuid": submodule_ids},
            )
            if not success:
                return self.send_error_response(sub_module_list)
            for submission_id in submission_ids:
                submission_data = submissions[submission_id]
                submission_data["sub_module"] = sub_module_list["data"].get(str(submission_data["sub_module"]["id"]))
                if submission_data["sub_module"]:
                    submission_data["course"] = submission_data["sub_module"].get("course")
        return response


class SubModuleFileSubmissionRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api view to retrieve submodule file submissions."""

    serializer_class = SubModuleFileSubmissionListSerializer
    queryset = SubModuleFileSubmission.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Overriden to include ccms details."""

        response = super().retrieve(request, *args, **kwargs)
        sub_module_details = response.data["data"]["sub_module"]
        if sub_module_details.get("is_ccms_obj"):
            success, data = get_ccms_retrieve_details(
                learning_type="course_submodule",
                instance_id=str(sub_module_details["id"]),
                request={"headers": request.headers},
            )
            if not success:
                return self.send_error_response(data)
            response.data["data"]["sub_module"] = data["data"]
        return response


class SubModuleFileSubmissionUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api view to update submodule file submission."""

    serializer_class = SubModuleFileSubmissionUpdateSerializer
    queryset = SubModuleFileSubmission.objects.all()


class FileSubmissionReattemptEnableApiView(AppAPIView):
    """Api view to enable the reattempt of sub module file submission."""

    def post(self, request, *args, **kwargs):
        """Handle on post."""

        tracker = get_object_or_404(CourseSubModuleTracker, id=self.kwargs["tracker_id"])
        if tracker.available_attempt and tracker.available_attempt > 0:
            return self.send_error_response("Reattempt not allowed.")
        tracker.available_attempt = 1
        tracker.save()
        return self.send_response("Success")
