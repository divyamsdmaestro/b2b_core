import csv
import io

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.access_control.fixtures import PolicyChoices
from apps.common.helpers import process_request_headers
from apps.common.serializers import AppSerializer
from apps.common.views.api import (
    AppAPIView,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    get_upload_api_view,
)
from apps.learning.helpers import process_and_save_uploaded_file
from apps.learning.models import Course, CourseImageModel, CourseResource
from apps.learning.serializers.v1 import (
    CourseCUDModelSerializer,
    CourseListModelSerializer,
    CourseResourceCreateModelSerializer,
    CourseResourceListModelSerializer,
    CourseRetrieveModelSerializer,
)
from apps.learning.tasks import CourseBulkUploadTask
from apps.learning.views.api.v1 import BaseLearningSkillRoleListApiViewSet
from apps.tenant_service.middlewares import get_current_db_name

CourseImageUploadAPIView = get_upload_api_view(meta_model=CourseImageModel, meta_fields=["id", "image"])


class CourseCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete courses."""

    serializer_class = CourseCUDModelSerializer
    queryset = Course.objects.alive()
    policy_slug = PolicyChoices.course_management


class CourseListApiViewSet(BaseLearningSkillRoleListApiViewSet):
    """Api viewset to list courses."""

    queryset = Course.objects.alive().order_by("created_at")
    serializer_class = CourseListModelSerializer
    policy_slug = PolicyChoices.course_management
    user_group_filter_key = "related_learning_catalogues__related_catalogue_relations__user_group__id__in"


class CourseRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Viewset to retrieve the particular course along with  module & sub_module details."""

    serializer_class = CourseRetrieveModelSerializer
    queryset = Course.objects.alive()
    policy_slug = PolicyChoices.course_management


class CourseCloneApiView(AppAPIView):
    """Api view to clone the given course."""

    class _Serializer(AppSerializer):
        """Serializer class for the same."""

        course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive())

    serializer_class = _Serializer
    policy_slug = PolicyChoices.course_management

    def post(self, request, *args, **kwargs):
        """Clone the course logic."""

        serializer = self.get_valid_serializer()
        course = serializer.validated_data["course"]
        request_headers = process_request_headers(request={"headers": dict(request.headers)})
        clone_details = course.clone(request_headers=request_headers)
        return self.send_response(data=clone_details)


class CourseResourceApiViewSet(AppModelCUDAPIViewSet):
    """Api view to upload the resources."""

    serializer_class = CourseResourceCreateModelSerializer
    queryset = CourseResource.objects.all()
    policy_slug = PolicyChoices.course_management

    def get_serializer_context(self):
        """Include the learning type."""

        context = super().get_serializer_context()
        context["learning_type"] = "course"
        return context


class CourseResourceListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the course resources."""

    serializer_class = CourseResourceListModelSerializer
    queryset = CourseResource.objects.all()
    policy_slug = PolicyChoices.course_management

    def get_queryset(self):
        """Overridden to provide the list of course resources."""

        course_pk = self.kwargs.get("course_pk", None)
        course_instance = get_object_or_404(Course, pk=course_pk)

        return course_instance.related_course_resources.all()


class CourseBulkUploadAPIView(AppAPIView):
    """API View to bulk upload courses from a CSV file."""

    policy_slug = PolicyChoices.course_management

    def post(self, request, *args, **kwargs):
        """Handle on post"""

        if not (uploaded_file := request.FILES.get("file")):
            return self.send_error_response(data="File not found")
        if not uploaded_file.name.endswith(".csv"):
            return self.send_error_response(data="Unsupported file format. Please upload a .csv file.")
        db_name = get_current_db_name()
        folder_path = f"apps/media/temp/{db_name}/course_bulk_upload"
        file_path = process_and_save_uploaded_file(uploaded_file, folder_path)
        CourseBulkUploadTask().run_task(file_path=file_path, db_name=db_name)
        return self.send_response()


class CourseBulkUploadSampleFileAPIView(AppAPIView):
    """API View to download sample bulk upload CSV file."""

    def get(self, request, *args, **kwargs):
        """Handle on get"""

        # Create a CSV response
        response = Response(
            headers={"Content-Disposition": 'attachment; filename="Course_Bulk_Upload_Template.csv"'},
            content_type="text/csv",
        )
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        data = [
            [
                "course_name",
                "course_description",
                "course_author",
                "course_category",
                "course_skill",
                "course_role",
                "course_start_date",
                "course_end_date",
                "course_code",
                "course_image_url",
                "course_language",
                "course_prerequisite",
                "course_proficiency",
                "course_highlight",
                "course_hashtag",
                "course_rating",
                "course_learning_points",
                "course_mml_sku_id",
                "course_vm_name",
                "course_is_feedback_enabled",
                "course_is_feedback_mandatory",
                "course_feedback_template",
                "course_is_rating_enabled",
                "course_is_dependencies_sequential",
                "course_is_popular",
                "course_is_trending",
                "course_is_recommended",
                "course_is_certificate_enabled",
                "course_certificate_id",
                "course_module_name",
                "course_module_description",
                "course_module_start_date",
                "course_module_end_date",
                "course_module_position",
                "course_module_is_mandatory",
                "course_sub_module_name",
                "course_sub_module_description",
                "course_sub_module_position",
                "course_sub_module_duration",
                "course_sub_module_url",
                "course_assessment_type",
                "course_assessment_name",
                "course_assessment_uuid",
                "course_assignment_type",
                "course_assignment_code",
            ],
            [
                "Data Engineering",
                "desc",
                "author name",
                "category test",
                "skill1,skill2",
                "role1,role2",
                "01/10/2023",
                "01/11/2023",
                "COU_12512",
                "https://irisdatacontainer.blob.core.windows.net/images/Course/dddb207a.png",
                "English",
                "Data science",
                "basic",
                "• Lorem Ipsum.\n• Vestibulum ante ipsum primis.\n• Pellentesque euismod eget turpis.",
                "#hastag1,#hastag2,#hastag3",
                "5",
                "10",
                "",
                "vm_name",
                "1",
                "1",
                "template_name",
                "1",
                "1",
                "1",
                "1",
                "1",
                "0",
                "",
                "coursemodule testing 1",
                "desc",
                "10/10/2023",
                "20/10/2023",
                "2",
                "1",
                "sub_module_testing 1",
                "desc",
                "1",
                "00:03:32",
                "https://irisstorageprod.blob.core.windows.net/packt/2023/January/V19593/video1_1.mp4?",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "Data Engineering",
                "desc",
                "author name",
                "category test",
                "skill1,skill2",
                "role1,role2",
                "01/10/2023",
                "01/11/2023",
                "COU_12512",
                "https://irisdatacontainer.blob.core.windows.net/images/Course/dddb207a.png",
                "English",
                "Data science",
                "basic",
                "• Lorem Ipsum.\n• Vestibulum ante ipsum primis.\n• Pellentesque euismod eget turpis.",
                "#hastag1,#hastag2,#hastag3",
                "5",
                "10",
                "",
                "vm_name",
                "1",
                "1",
                "template_name",
                "1",
                "1",
                "1",
                "1",
                "1",
                "0",
                "",
                "coursemodule testing 1",
                "desc",
                "10/10/2023",
                "20/10/2023",
                "2",
                "1",
                "",
                "",
                "",
                "",
                "",
                "dependent_assessment",
                "assessment for coursemodule testing 1",
                "2039f75c-5e20-4ea9-9bd6-094294c4c587",
                "dependent_assignment",
                "ASSIGN1010",
            ],
            [
                "Data Engineering",
                "desc",
                "author name",
                "category test",
                "skill1,skill2",
                "role1,role2",
                "01/10/2023",
                "01/11/2023",
                "COU_12512",
                "https://irisdatacontainer.blob.core.windows.net/images/Course/dddb207a.png",
                "English",
                "Data science",
                "basic",
                "• Lorem Ipsum.\n• Vestibulum ante ipsum primis.\n• Pellentesque euismod eget turpis.",
                "#hastag1,#hastag2,#hastag3",
                "5",
                "10",
                "",
                "vm_name",
                "1",
                "1",
                "template_name",
                "1",
                "1",
                "1",
                "1",
                "1",
                "0",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "final_assessment",
                "final assess for Data Engineering",
                "2039f75c-5e20-4ea9-9bd6-094294c4c587",
                "final_assignment",
                "ASSIGN2020",
            ],
        ]
        # Write data to the CSV buffer
        for row in data:
            writer.writerow(row)
        # Reset the buffer position to the beginning
        csv_buffer.seek(0)
        response.content = csv_buffer.read()
        return response
