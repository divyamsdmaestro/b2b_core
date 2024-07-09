from django.db.models import Q
from rest_framework.generics import get_object_or_404

from apps.common.views.api import (
    AppAPIView,
    AppModelCreateAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
)
from apps.learning.config import AssessmentTypeChoices, CommonLearningAssignmentTypeChoices
from apps.learning.models import LearningPath
from apps.my_learning.config import EnrollmentTypeChoices
from apps.my_learning.helpers import get_ccms_list_details, get_ccms_tracker_details
from apps.my_learning.models import Enrollment, FeedbackResponse, UserLearningPathTracker
from apps.my_learning.serializers.v1 import (
    BaseEnrollmentListModelSerializer,
    UserLearningPathCourseListSerializer,
    UserLearningPathListSerializer,
    UserLearningPathRetrieveSerializer,
    UserLearningPathTrackerCreateModelSerializer,
    UserLPAssessmentListSerializer,
    UserLPAssignmentListSerializer,
)
from apps.my_learning.serializers.v1.tracker.assignment import UserAssignmentTrackerListSerializer
from apps.my_learning.serializers.v1.tracker.learning_path.assessment import LPATrackerListSerializer
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet


class UserLearningPathListApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """Viewset to list the learning_path with enrolled_details.."""

    serializer_class = UserLearningPathListSerializer
    queryset = LearningPath.objects.unarchived()

    def sorting_options(self):
        """Returns the sorting options."""

        return {
            "-related_user_learning_path_trackers__last_accessed_on": "Accessed Recently",
            "related_user_learning_path_trackers__valid_till": "Nearing Deadline",
        }


class UserLearningPathRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api viewset to retrieve learning_path along with the courses."""

    serializer_class = UserLearningPathRetrieveSerializer
    queryset = LearningPath.objects.alive()


class UserLearningPathTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """Learning path tracker create api."""

    serializer_class = UserLearningPathTrackerCreateModelSerializer
    queryset = UserLearningPathTracker.objects.all()


class UserLPCourseListApiViewSet(AppModelListAPIViewSet):
    """Learning path course list api view set."""

    serializer_class = UserLearningPathCourseListSerializer

    def get_queryset(self):
        """Returns the list of courses based on lp."""

        lp = self.kwargs.get("id")
        lp_instance = get_object_or_404(LearningPath, id=lp)
        return lp_instance.related_learning_path_courses.filter(course__is_deleted=False).order_by("sequence")


class UserLPFinalEvaluationListApiView(AppAPIView):
    """List api view for learning_path final assignments & assessments."""

    def get(self, request, *args, **kwargs):
        """Returns the final assignments & assessments."""

        is_ccms_obj = request.query_params.get("is_ccms_obj")
        lp_id = request.query_params.get("learning_path")
        request_headers = {"headers": dict(request.headers)}
        user = self.get_user()
        if is_ccms_obj:
            params = {"learning_path__uuid": lp_id}
            assessment_success, final_assessments = get_ccms_list_details(
                learning_type="lp_assessment", request=request_headers, params=params
            )
            assignment_success, final_assignments = get_ccms_list_details(
                learning_type="lp_assignment", request=request_headers, params=params
            )
            if assignment_success and assessment_success:
                assessments = final_assessments["data"].get("results", [])
                assignments = final_assignments["data"].get("results", [])
                for assessment in assessments:
                    assessment_uuid = assessment["uuid"]
                    assessment_tracker = user.related_lp_assessment_trackers.filter(
                        is_ccms_obj=True, ccms_id=assessment_uuid
                    ).first()
                    assessment["tracker_detail"] = (
                        LPATrackerListSerializer(assessment_tracker).data if assessment_tracker else None
                    )
                for assignment in assignments:
                    assignment_uuid = assignment["assignment"]["uuid"]
                    assignment_tracker = user.related_assignment_trackers.filter(
                        is_ccms_obj=True, ccms_id=assignment_uuid
                    ).first()
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
        else:
            learning_path = get_object_or_404(LearningPath, id=lp_id)
            final_assignments = learning_path.related_lp_assignments.filter(
                type=CommonLearningAssignmentTypeChoices.final_assignment
            ).order_by("sequence", "created_at")
            final_assessments = learning_path.related_lp_assessments.filter(
                type=AssessmentTypeChoices.final_assessment
            ).order_by("sequence", "created_at")
            context = self.get_serializer_context()
            context["lp_tracker"] = user.related_user_learning_path_trackers.filter(
                learning_path=learning_path
            ).first()
            return self.send_response(
                {
                    "final_assignments": UserLPAssignmentListSerializer(
                        final_assignments, many=True, context=context
                    ).data,
                    "final_assessments": UserLPAssessmentListSerializer(
                        final_assessments, many=True, context=context
                    ).data,
                }
            )


class UserCCMSLPListApiView(AppAPIView):
    """LearningPath list from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS courses with enrollment details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        success, data = get_ccms_list_details(
            learning_type=EnrollmentTypeChoices.learning_path, request=request_headers, params=request_params
        )
        if success:
            results = data["data"]["results"]
            for result in results:
                lp_uuid = result["uuid"]
                user = self.get_user()
                user_groups = user.related_user_groups.all().values_list("id", flat=True)
                enrollment_instance = Enrollment.objects.filter(
                    Q(user_group__in=user_groups) | Q(user=user),
                    learning_type=EnrollmentTypeChoices.learning_path,
                    ccms_id=lp_uuid,
                ).first()
                result["enrolled_details"] = (
                    BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
                    if enrollment_instance
                    else None
                )
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.learning_path, ccms_id=lp_uuid
                )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])


class UserCCMSLPCourseListApiView(AppAPIView):
    """LP course list api view from ccms with tracker details."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS lp courses with tracker details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        lp_id = self.kwargs.get("lp_id")
        user = self.get_user()
        request_params.update({"learning_path__uuid": lp_id})
        success, data = get_ccms_list_details(
            learning_type="lp_course", request=request_headers, params=request_params
        )
        if success:
            results = data["data"]["results"]
            for result in results:
                course_uuid = result["course"]["uuid"]
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.course, ccms_id=course_uuid
                )
                assessments = result["assessments"]
                for assessment in assessments:
                    assessment_uuid = assessment["uuid"]
                    assessment_tracker = user.related_lp_assessment_trackers.filter(
                        is_ccms_obj=True, ccms_id=assessment_uuid
                    ).first()
                    assessment["tracker_detail"] = (
                        LPATrackerListSerializer(assessment_tracker).data if assessment_tracker else None
                    )
                assignments = result["assignments"]
                for assignment in assignments:
                    assignment_uuid = assignment["assignment"]["uuid"]
                    assignment_tracker = user.related_assignment_trackers.filter(
                        is_ccms_obj=True, ccms_id=assignment_uuid
                    ).first()
                    assignment["tracker_detail"] = (
                        UserAssignmentTrackerListSerializer(assignment_tracker).data if assignment_tracker else None
                    )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])


class UserCCMSLPRetrieveApiView(AppAPIView):
    """LP retrieve from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS learning_path with enrollment details."""

        from apps.learning.helpers import get_ccms_retrieve_details

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        lp_id = kwargs.get("uuid")
        success, data = get_ccms_retrieve_details(
            learning_type=EnrollmentTypeChoices.learning_path,
            instance_id=lp_id,
            request=request_headers,
            params=request_params,
        )
        if success:
            result = data["data"]
            if result:
                lp_id = result["uuid"]
                user = self.get_user()
                user_groups = user.related_user_groups.all().values_list("id", flat=True)
                enrollment_instance = Enrollment.objects.filter(
                    Q(user_group__in=user_groups) | Q(user=user),
                    learning_type=EnrollmentTypeChoices.learning_path,
                    ccms_id=lp_id,
                ).first()
                result["enrolled_details"] = (
                    BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
                    if enrollment_instance
                    else None
                )
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.learning_path, ccms_id=lp_id
                )
                result["is_feedback_given"] = FeedbackResponse.objects.filter(
                    learning_type=EnrollmentTypeChoices.learning_path,
                    learning_type_id=lp_id,
                    template_ccms_id__in=result["feedback_template_uuids"],
                    user=user,
                ).exists()
            return self.send_response(result)
        else:
            return self.send_error_response(data["data"])
