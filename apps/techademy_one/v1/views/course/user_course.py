from apps.access.models import User
from apps.common.idp_service import idp_admin_auth_token
from apps.common.views.api import AppAPIView, NonAuthenticatedAPIMixin
from apps.learning.helpers import get_ccms_retrieve_details
from apps.learning.models import Course
from apps.my_learning.config import EnrollmentTypeChoices, LearningStatusChoices
from apps.my_learning.models import Enrollment
from apps.my_learning.models.tracker.course.course import UserCourseTracker
from apps.techademy_one.v1.serializers import T1CourseListSerializer, T1UserTopCourseSerializer
from apps.tenant.models import Tenant


class T1UserTopCourseAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to send User's top 5 courses for different progres statuses."""

    serializer_class = T1UserTopCourseSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        data = self.get_valid_serializer().validated_data
        tenant_id, user_id = data["tenant_id"], data["user_id"]
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Tenant not found."})
        tenant.activate_db()
        user = User.objects.filter(uuid=user_id).first()
        if not user:
            return self.send_error_response(data={"message": "User not found."})

        enrollments = Enrollment.objects.filter(user=user, learning_type=EnrollmentTypeChoices.course)
        top_courses = {
            LearningStatusChoices.not_started: enrollments.filter(learning_status=LearningStatusChoices.not_started)[
                :5
            ],
            LearningStatusChoices.started: enrollments.filter(learning_status=LearningStatusChoices.started)[:5],
            LearningStatusChoices.in_progress: enrollments.filter(learning_status=LearningStatusChoices.in_progress)[
                :5
            ],
            LearningStatusChoices.completed: enrollments.filter(learning_status=LearningStatusChoices.completed)[:5],
        }

        auth_token = idp_admin_auth_token(raise_drf_error=False)
        top_courses_data = {}
        for status, course_enrollments in top_courses.items():
            course_data = {}
            for course_enrollment in course_enrollments:
                if course_enrollment.is_ccms_obj:
                    course_name = self.get_ccms_course_name(course_enrollment.ccms_id, auth_token)
                else:
                    course_name = course_enrollment.course.name
                tracker = UserCourseTracker.objects.filter(enrollment=course_enrollment).first()
                progress = tracker.progress if tracker else 0
                course_data[course_name] = progress
            top_courses_data[status] = course_data
        return self.send_response(data=top_courses_data)

    @staticmethod
    def get_ccms_course_name(ccms_id, auth_token):
        """Call CCMS Service to get course details."""

        request_headers_data = {"headers": {"Idp-Token": auth_token}}
        success, data = get_ccms_retrieve_details(
            learning_type=EnrollmentTypeChoices.course, instance_id=str(ccms_id), request=request_headers_data
        )
        if success:
            return data["data"]["name"]
        return "CCMS Course"


class T1CourseListAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to send recently created top 10 courses."""

    def get(self, request, *args, **kwargs):
        """Logic for the same."""

        tenant_id = request.query_params.get("tenant_id")
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Tenant not found."})
        tenant.activate_db()
        courses = Course.objects.active().order_by("-created_at")[:10]
        course_data = T1CourseListSerializer(courses, many=True).data
        return self.send_response(data={"course_details": course_data})
