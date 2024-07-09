from rest_framework.generics import get_object_or_404

from apps.common.pagination import TempPagination
from apps.common.views.api import AppAPIView, AppModelCreateAPIViewSet, AppModelListAPIViewSet
from apps.learning.models import CourseModule
from apps.my_learning.helpers import get_ccms_list_details
from apps.my_learning.models import CourseModuleTracker, UserCourseTracker
from apps.my_learning.serializers.v1 import (
    CATrackerListSerializer,
    CourseModuleTrackerCreateSerializer,
    CourseModuleTrackerListSerializer,
    UserAssignmentTrackerListSerializer,
    UserCourseModuleListSerializer,
)


class UserCourseModuleListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the course modules."""

    serializer_class = UserCourseModuleListSerializer
    pagination_class = TempPagination

    def get_serializer_context(self):
        """Overridden to set the serializer context"""

        tracker_pk = self.kwargs.get("tracker_pk")
        tracker_instance = get_object_or_404(UserCourseTracker, pk=tracker_pk, user=self.get_user())
        context = super().get_serializer_context()
        context["course_tracker"] = tracker_instance
        return context

    def get_queryset(self):
        """Returns the course module trackers."""

        tracker_instance = self.get_serializer_context()["course_tracker"]
        if not tracker_instance.is_ccms_obj:
            return (
                CourseModule.objects.prefetch_related("related_course_module_trackers")
                .alive()
                .filter(course=tracker_instance.course)
                .order_by("sequence", "created_at")
            )


class CourseModuleTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """View for course module tracker cd."""

    serializer_class = CourseModuleTrackerCreateSerializer
    queryset = CourseModuleTracker.objects.all()


class UserCCMSCourseModuleListApiView(AppAPIView):
    """Course module list api view from ccms with tracker details."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS course modules with tracker details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        tracker_pk = self.kwargs.get("tracker_pk")
        tracker_instance = get_object_or_404(UserCourseTracker, pk=tracker_pk, user=self.get_user())
        if not tracker_instance.is_ccms_obj:
            return self.send_error_response("Detail not found")
        request_params.update({"course": tracker_instance.ccms_id})
        success, data = get_ccms_list_details(
            request=request_headers, learning_type="course_module", params=request_params
        )
        if success:
            results = data["data"]["results"]
            for result in results:
                module_uuid = result["uuid"]
                module_tracker = tracker_instance.related_course_module_trackers.filter(
                    is_ccms_obj=True, ccms_id=module_uuid
                ).first()
                result["tracker_details"] = (
                    CourseModuleTrackerListSerializer(module_tracker).data if module_tracker else None
                )
                assessments = result["assessments"]
                for assessment in assessments:
                    assessment_uuid = assessment["uuid"]
                    if module_tracker:
                        assessment_tracker = module_tracker.related_course_assessment_trackers.filter(
                            is_ccms_obj=True, ccms_id=assessment_uuid
                        ).first()
                        assessment["tracker_detail"] = (
                            CATrackerListSerializer(assessment_tracker).data if assessment_tracker else None
                        )
                assignments = result["assignments"]
                for assignment in assignments:
                    assignment_uuid = assignment["assignment"]["uuid"]
                    assignment_tracker = (
                        self.get_user()
                        .related_assignment_trackers.filter(is_ccms_obj=True, ccms_id=assignment_uuid)
                        .first()
                    )
                    assignment["tracker_detail"] = (
                        UserAssignmentTrackerListSerializer(assignment_tracker).data if assignment_tracker else None
                    )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])
