from django.db.models import Q
from rest_framework.generics import get_object_or_404

from apps.common.mml_communicator import mml_vm_creation
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.config import AssessmentTypeChoices, CommonLearningAssignmentTypeChoices
from apps.learning.models import Course
from apps.my_learning.config import EnrollmentTypeChoices
from apps.my_learning.helpers import get_ccms_list_details, get_ccms_tracker_details
from apps.my_learning.models import Enrollment, FeedbackResponse, UserCourseTracker
from apps.my_learning.serializers.v1 import (
    BaseEnrollmentListModelSerializer,
    CATrackerListSerializer,
    UserAssignmentTrackerListSerializer,
    UserCourseAssessmentListSerializer,
    UserCourseAssignmentListSerializer,
    UserCourseListSerializer,
    UserCourseRetrieveModelSerializer,
    UserCourseTrackerCreateModelSerializer,
)
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet


class UserCourseListApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """Viewset to list the enrolled course of the user."""

    serializer_class = UserCourseListSerializer
    queryset = Course.objects.unarchived()

    def sorting_options(self):
        """Returns the sorting options."""

        return {
            "-related_user_course_trackers__last_accessed_on": "Accessed Recently",
            "related_user_course_trackers__valid_till": "Nearing Deadline",
        }


class UserCourseDetailedRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Viewset to retrieve the particular course along with  module & sub_module details."""

    serializer_class = UserCourseRetrieveModelSerializer
    queryset = Course.objects.alive()


class UserCourseTrackerCreateApiViewSet(AppModelCUDAPIViewSet):
    """View for course tracker cud."""

    serializer_class = UserCourseTrackerCreateModelSerializer
    queryset = UserCourseTracker.objects.all()


class UserCourseMMLVMStartAPIView(AppAPIView):
    """Api view to start the mml vm."""

    def post(self, request, *args, **kwargs):
        """Returns the VM details."""

        course_tracker_id = self.kwargs.get("tracker_pk", None)
        course_tracker_instance = get_object_or_404(UserCourseTracker, id=course_tracker_id, user=self.get_user())
        mml_sku_id = getattr(course_tracker_instance.course, "mml_sku_id", None)
        vm_name = getattr(course_tracker_instance.course, "vm_name", None)
        kc_flag = False
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            kc_flag = True
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        if not mml_sku_id:
            return self.send_error_response({"detail": "Labs not available for this course."})
        success, data, headers = mml_vm_creation(idp_token, mml_sku_id, vm_name, kc_flag)
        if success:
            data["headers"] = headers
            return self.send_response(data)
        else:
            return self.send_error_response(data)


class UserCourseFinalEvaluationListApiView(AppAPIView):
    """List api view for course final assignments & assessments."""

    def get(self, request, *args, **kwargs):
        """Returns the final assignments & assessments."""

        tracker_pk = kwargs.get("tracker_pk", None)
        course_tracker = get_object_or_404(UserCourseTracker, pk=tracker_pk)
        request_headers = {"headers": dict(request.headers)}
        if not course_tracker.is_ccms_obj:
            final_assignments = course_tracker.course.related_course_assignments.filter(
                type=CommonLearningAssignmentTypeChoices.final_assignment
            ).order_by("sequence", "created_at")
            final_assessments = course_tracker.course.related_course_assessments.filter(
                type=AssessmentTypeChoices.final_assessment
            ).order_by("sequence", "created_at")
            context = self.get_serializer_context()
            context["course_tracker"] = course_tracker
            return self.send_response(
                {
                    "final_assignments": UserCourseAssignmentListSerializer(
                        final_assignments, many=True, context=context
                    ).data,
                    "final_assessments": UserCourseAssessmentListSerializer(
                        final_assessments, many=True, context=context
                    ).data,
                }
            )
        else:
            params = {"course__uuid": course_tracker.ccms_id}
            assessment_success, final_assessments = get_ccms_list_details(
                request=request_headers, learning_type="course_assessment", params=params
            )
            assignment_success, final_assignments = get_ccms_list_details(
                request=request_headers, learning_type="course_assignment", params=params
            )
            if assignment_success and assessment_success:
                assessments = final_assessments["data"].get("results", [])
                assignments = final_assignments["data"].get("results", [])
                for assessment in assessments:
                    assessment_uuid = assessment["uuid"]
                    assessment_tracker = course_tracker.related_course_assessment_trackers.filter(
                        is_ccms_obj=True, ccms_id=assessment_uuid
                    ).first()
                    assessment["tracker_detail"] = (
                        CATrackerListSerializer(assessment_tracker).data if assessment_tracker else None
                    )
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
                return self.send_response(
                    {
                        "final_assignments": assignments,
                        "final_assessments": assessments,
                    }
                )
            else:
                return self.send_error_response("Something went wrong. Contact us.")


class UserCCMSCourseListApiView(AppAPIView):
    """Course list from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS courses with enrollment details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        success, data = get_ccms_list_details(
            request=request_headers, learning_type=EnrollmentTypeChoices.course, params=request_params
        )
        if success:
            results = data["data"]["results"]
            for result in results:
                course_uuid = result["uuid"]
                user = self.get_user()
                user_groups = user.related_user_groups.all().values_list("id", flat=True)
                enrollment_instance = Enrollment.objects.filter(
                    Q(user_group__in=user_groups) | Q(user=user),
                    learning_type=EnrollmentTypeChoices.course,
                    ccms_id=course_uuid,
                ).first()
                result["enrolled_details"] = (
                    BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
                    if enrollment_instance
                    else None
                )
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.course, ccms_id=course_uuid
                )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])


class UserCCMSCourseRetrieveApiView(AppAPIView):
    """Course retrieve from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS course with enrollment details."""

        from apps.learning.helpers import get_ccms_retrieve_details

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        course_id = kwargs.get("uuid")
        success, data = get_ccms_retrieve_details(
            learning_type=EnrollmentTypeChoices.course,
            instance_id=course_id,
            request=request_headers,
            params=request_params,
        )
        if success:
            result = data["data"]
            if result:
                course_uuid = result["uuid"]
                user = self.get_user()
                user_groups = user.related_user_groups.all().values_list("id", flat=True)
                enrollment_instance = Enrollment.objects.filter(
                    Q(user_group__in=user_groups) | Q(user=user),
                    learning_type=EnrollmentTypeChoices.course,
                    ccms_id=course_uuid,
                ).first()
                result["enrolled_details"] = (
                    BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
                    if enrollment_instance
                    else None
                )
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.course, ccms_id=course_uuid
                )
                result["is_feedback_given"] = FeedbackResponse.objects.filter(
                    learning_type=EnrollmentTypeChoices.course,
                    learning_type_id=course_uuid,
                    template_ccms_id__in=result["feedback_template_uuids"],
                    user=user,
                ).exists()
            return self.send_response(result)
        else:
            return self.send_error_response(data["data"])
