from django.db.models import Q
from rest_framework.generics import get_object_or_404

from apps.common.views.api import (
    AppAPIView,
    AppModelCreateAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
)
from apps.learning.models import AdvancedLearningPath
from apps.my_learning.config import EnrollmentTypeChoices
from apps.my_learning.helpers import get_ccms_list_details, get_ccms_tracker_details
from apps.my_learning.models import Enrollment, FeedbackResponse, UserALPTracker
from apps.my_learning.serializers.v1 import (
    BaseEnrollmentListModelSerializer,
    UserAdvancedLearningPathListSerializer,
    UserAdvancedLearningPathRetrieveModelSerializer,
    UserALPLearningPathListSerializer,
    UserALPTrackerCreateModelSerializer,
)
from apps.my_learning.views.api.v1 import BaseMyLearningSkillRoleListApiViewSet


class UserALPListModelApiViewSet(BaseMyLearningSkillRoleListApiViewSet):
    """View to list the advanced learning path."""

    serializer_class = UserAdvancedLearningPathListSerializer
    queryset = AdvancedLearningPath.objects.unarchived()

    def sorting_options(self):
        """Returns the sorting options."""

        return {
            "-related_user_alp_trackers__last_accessed_on": "Accessed Recently",
            "related_user_alp_trackers__valid_till": "Nearing Deadline",
        }


class UserALPRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """View to retrieve the advanced learning path."""

    serializer_class = UserAdvancedLearningPathRetrieveModelSerializer
    queryset = AdvancedLearningPath.objects.alive()


class UserAlpTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """View to add the advanced learning path tracker."""

    serializer_class = UserALPTrackerCreateModelSerializer
    queryset = UserALPTracker.objects.all()


class UserALPLearningPathListApiViewSet(AppModelListAPIViewSet):
    """ALP Learning path list api view set."""

    serializer_class = UserALPLearningPathListSerializer

    def get_queryset(self):
        """Returns the list of lp based on alp."""

        alp = self.kwargs.get("id")
        alp_instance = get_object_or_404(AdvancedLearningPath, id=alp)
        return alp_instance.related_alp_learning_paths.filter(learning_path__is_deleted=False).order_by("sequence")


class UserCCMSALPListApiView(AppAPIView):
    """AdvancedLearningPath list from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS alp's with enrollment details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        success, data = get_ccms_list_details(
            learning_type=EnrollmentTypeChoices.advanced_learning_path, request=request_headers, params=request_params
        )
        if success:
            results = data["data"]["results"]
            for result in results:
                alp_uuid = result["uuid"]
                user = self.get_user()
                user_groups = user.related_user_groups.all().values_list("id", flat=True)
                enrollment_instance = Enrollment.objects.filter(
                    Q(user_group__in=user_groups) | Q(user=user),
                    learning_type=EnrollmentTypeChoices.advanced_learning_path,
                    ccms_id=alp_uuid,
                ).first()
                result["enrolled_details"] = (
                    BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
                    if enrollment_instance
                    else None
                )
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.advanced_learning_path, ccms_id=alp_uuid
                )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])


class UserCCMSALPRetrieveApiView(AppAPIView):
    """ALP retrieve from ccms."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS alp with enrollment details."""

        from apps.learning.helpers import get_ccms_retrieve_details

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        alp_id = kwargs.get("uuid")
        success, data = get_ccms_retrieve_details(
            learning_type=EnrollmentTypeChoices.advanced_learning_path,
            instance_id=alp_id,
            request=request_headers,
            params=request_params,
        )
        if success:
            result = data["data"]
            if result:
                alp_id = result["uuid"]
                user = self.get_user()
                user_groups = user.related_user_groups.all().values_list("id", flat=True)
                enrollment_instance = Enrollment.objects.filter(
                    Q(user_group__in=user_groups) | Q(user=user),
                    learning_type=EnrollmentTypeChoices.advanced_learning_path,
                    ccms_id=alp_id,
                ).first()
                result["enrolled_details"] = (
                    BaseEnrollmentListModelSerializer(enrollment_instance, context=self.get_serializer_context()).data
                    if enrollment_instance
                    else None
                )
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.advanced_learning_path, ccms_id=alp_id
                )
                result["is_feedback_given"] = FeedbackResponse.objects.filter(
                    learning_type=EnrollmentTypeChoices.advanced_learning_path,
                    learning_type_id=alp_id,
                    template_ccms_id__in=result["feedback_template_uuids"],
                    user=user,
                ).exists()
            return self.send_response(result)
        else:
            return self.send_error_response(data["data"])


class UserCCMSALPLearningPathListApiView(AppAPIView):
    """ALP learning_path list api view from ccms with tracker details."""

    def get(self, request, *args, **kwargs):
        """Returns the CCMS alp learning paths with tracker details."""

        request_params = request.query_params.dict()
        request_headers = {"headers": dict(request.headers)}
        alp_id = self.kwargs.get("alp_id")
        user = self.get_user()
        request_params.update({"advanced_learning_path__uuid": alp_id})
        success, data = get_ccms_list_details(learning_type="alp_lp", request=request_headers, params=request_params)
        if success:
            results = data["data"]["results"]
            for result in results:
                lp_uuid = result["learning_path"]["uuid"]
                result["tracker_detail"] = get_ccms_tracker_details(
                    user=user, learning_type=EnrollmentTypeChoices.learning_path, ccms_id=lp_uuid
                )
            return self.send_response(data["data"])
        else:
            return self.send_error_response(data["data"])
