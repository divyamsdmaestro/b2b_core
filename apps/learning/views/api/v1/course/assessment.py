from django.conf import settings
from django.db.models import Q
from rest_framework.decorators import action

from apps.common.communicator import get_request
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import CourseAssessment
from apps.learning.serializers.v1 import CourseAssessmentCUDModelSerializer, CourseAssessmentListModelSerializer
from apps.tenant_service.middlewares import get_current_tenant_details, get_current_tenant_idp_id


class CourseAssessmentCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset for course assessments."""

    queryset = CourseAssessment.objects.all()
    serializer_class = CourseAssessmentCUDModelSerializer


class CourseAssessmentListAPiViewSet(AppModelListAPIViewSet):
    """Api viewset to list course assessments."""

    serializer_class = CourseAssessmentListModelSerializer
    queryset = CourseAssessment.objects.order_by("sequence", "created_at")
    filterset_fields = ["type", "module"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = self.serializer_class().get_filter_meta()
        return self.send_response(data)

    def get_queryset(self):
        """Overridden to filter the value based on query_params."""

        course = self.request.query_params.get("course")
        entire_ca = self.request.query_params.get("entire_ca")
        if course and entire_ca:
            return self.queryset.filter(Q(module__course=course) | Q(course=course))
        elif course:
            return self.queryset.filter(course=course)
        else:
            return self.queryset


class CourseAssessmentRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Course assessment retrieve API viewset."""

    serializer_class = CourseAssessmentListModelSerializer
    queryset = CourseAssessment.objects.all()


class YakshaAssessmentListApiView(AppAPIView):
    """Api view to list yaksha assessments."""

    def get(self, request, *args, **kwargs):
        """Returns the yaksha assessments."""

        request_headers = None
        tenant_details = get_current_tenant_details()
        if "kc-token" in request.headers:
            idp_token = request.headers.get("kc-token", None)
            service = "YAKSHA_ONE"
            request_headers = {"X-Tenant": tenant_details.get("tenancy_name", None)}
        else:
            idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
            service = "YAKSHA"
        success, data = get_request(
            service=service,
            url_path=settings.YAKSHA_CONFIG["get_assessments"],
            auth_token=idp_token,
            params={"tenantId": get_current_tenant_idp_id()},
            headers=request_headers,
        )
        if success:
            return self.send_response(data["result"])
        return self.send_error_response("Something went wrong. Contact us.")
