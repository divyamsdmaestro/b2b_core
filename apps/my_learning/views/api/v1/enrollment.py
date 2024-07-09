from io import BytesIO

import openpyxl
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.access.models import User
from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer
from apps.access_control.config import RoleTypeChoices
from apps.access_control.fixtures import PolicyChoices
from apps.access_control.models import UserGroup
from apps.common.helpers import get_sorting_meta
from apps.common.views.api import (
    AppAPIView,
    AppModelCreateAPIViewSet,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelUpdateAPIViewSet,
)
from apps.common.views.api.base import SortingMixin
from apps.learning.helpers import process_and_save_uploaded_file
from apps.my_learning.config import ApprovalTypeChoices, EnrollmentTypeChoices, LearningStatusChoices
from apps.my_learning.models import Enrollment, EnrollmentReminder
from apps.my_learning.serializers.v1 import (
    EnrollmentListModelSerializer,
    EnrollmentReminderCUDModelSerializer,
    EnrollmentReminderListModelSerializer,
    UserBulkEnrollSerializer,
    UserEnrollmentCreateModelSerializer,
    UserEnrollmentListModelSerializer,
    UserEnrollmentUpdateModelSerializer,
    tracker_related_fields,
)
from apps.my_learning.tasks import BulkUnenrollmentTask, EnrollmentBulkUploadTask, UserBulkEnrollTask
from apps.tenant_service.middlewares import get_current_db_name


class UserEnrollmentCreateApiViewSet(AppModelCreateAPIViewSet):
    """Create api for user enrollment."""

    serializer_class = UserEnrollmentCreateModelSerializer
    queryset = Enrollment.objects.all()

    def destroy(self, request, *args, **kwargs):
        """Delete the user enrollment."""

        instance = self.get_object()
        user = self.get_user()
        if instance.approval_type == ApprovalTypeChoices.self_enrolled:
            if user != instance.user and user.current_role.role_type not in [
                RoleTypeChoices.manager,
                RoleTypeChoices.admin,
            ]:
                return self.send_error_response("Invalid action.")
        else:
            if user == instance.user or user.current_role.role_type not in [
                RoleTypeChoices.manager,
                RoleTypeChoices.admin,
            ]:
                return self.send_error_response("Only self-enrollment can be unenrolled.")
        instance.remove_dependencies()
        instance.delete()
        return self.send_response("Success")


class EnrollmentListApiViewSet(SortingMixin, AppModelListAPIViewSet):
    """List api view for user enrollments."""

    serializer_class = EnrollmentListModelSerializer
    queryset = Enrollment.objects.all()
    filterset_fields = [
        "learning_type",
        "course",
        "learning_path",
        "advanced_learning_path",
        "skill_traveller",
        "playground",
        "playground_group",
        "assignment",
        "assignment_group",
        "action",
        "approval_type",
        "is_enrolled",
        "learning_status",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "course__name",
        "learning_path__name",
        "advanced_learning_path__name",
        "skill_traveller__name",
        "playground__name",
        "playground_group__name",
    ]
    policy_slug = PolicyChoices.enrollment_management

    def get_queryset(self):
        """Filter queryset based on manager's user groups."""

        user = self.get_user()
        queryset = super().get_queryset()
        if enrollment_type := self.request.query_params.get("enrollment_type"):
            if enrollment_type == "user":
                queryset = queryset.exclude(user=None)
            elif enrollment_type == "user_group":
                queryset = queryset.exclude(user_group=None)
            else:
                return queryset.none()
        if not user.current_role or user.current_role.role_type not in [
            RoleTypeChoices.admin,
            RoleTypeChoices.manager,
        ]:
            return queryset.none()
        if user.current_role.role_type == RoleTypeChoices.admin:
            return queryset
        return queryset.filter(
            Q(user_group__id__in=user.related_user_groups.all().values_list("id", flat=True))
            | Q(user__related_user_groups__id__in=user.related_user_groups.all().values_list("id", flat=True))
        )

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        data = {}
        if learning_type := self.request.query_params.get("learning_type"):
            sorting_options = {
                f"{learning_type}__name": "A to Z",
                f"-{learning_type}__name": "Z to A",
                "end_date": "Nearing Deadline",
            }
            user_tracker_key = (
                "-related_user_alp_trackers__last_accessed_on"
                if learning_type == "advanced_learning_path"
                else f"-related_user_{learning_type}_trackers__last_accessed_on"
            )
            sorting_options[user_tracker_key] = "Accessed Recently"
            data["sort_by"] = get_sorting_meta(sorting_options)
        return self.send_response(data)


class EnrollmentUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api view to update the enrollments."""

    serializer_class = UserEnrollmentUpdateModelSerializer
    queryset = Enrollment.objects.all()


class UserEnrollmentListApiViewSet(AppModelListAPIViewSet):
    """Api view to list user enrollment based on user."""

    serializer_class = UserEnrollmentListModelSerializer
    filterset_fields = ["learning_type"]
    search_fields = [
        "course__name",
        "learning_path__name",
        "advanced_learning_path__name",
        "skill_traveller__name",
        "playground__name",
        "playground_group__name",
    ]
    policy_slug = PolicyChoices.enrollment_management

    def get_queryset(self):
        """Overridden to provide a user enrolled objects."""

        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        enrollments = Enrollment.objects.filter(Q(user_group__in=user_groups) | Q(user=user)).distinct(
            "course",
            "learning_path",
            "advanced_learning_path",
            "skill_traveller",
            "skill_ontology",
            "playground",
            "playground_group",
            "assignment",
            "assignment_group",
            "ccms_id",
        )
        learning_status = self.request.query_params.get("learning_status")
        learning_type = self.request.query_params.get("learning_type")
        if learning_type and learning_type != EnrollmentTypeChoices.skill_ontology:
            enrollments = enrollments.filter(
                Q(**{"learning_type": learning_type, f"{learning_type}__is_retired": False, "is_ccms_obj": False})
                | Q(is_ccms_obj=True)
            )
        if learning_status and learning_type in tracker_related_fields:
            tracker = tracker_related_fields[learning_type]
            match learning_status:
                case LearningStatusChoices.not_started:
                    filter = {f"{tracker}__isnull": True}
                case LearningStatusChoices.in_progress:
                    filter = {f"{tracker}__is_completed": False}
                case LearningStatusChoices.completed:
                    filter = {f"{tracker}__is_completed": True}
                case _:
                    return enrollments
            enrollments = enrollments.filter(**filter)
        return enrollments


class UserBulkEnrollApiView(AppAPIView):
    """Api view to bulk enroll the users."""

    serializer_class = UserBulkEnrollSerializer
    policy_slug = PolicyChoices.enrollment_management

    def post(self, request, *args, **kwargs):
        """Api view to bulk enroll the users."""

        token = request.headers.get("idp-token")
        self.get_valid_serializer()
        UserBulkEnrollTask().run_task(
            data=self.get_request().data,
            authenticated_user=self.get_user().id,
            db_name=get_current_db_name(),
            token=token,
            request={"headers": dict(request.headers)},
        )
        return self.send_response("success")


class EnrolledUserListApiViewSet(AppModelListAPIViewSet):
    """List api view for enrolled users."""

    serializer_class = SimpleUserReadOnlyModelSerializer
    queryset = User.objects.alive()

    def get_queryset(self):
        """Overriden to return a queryset of enrolled users of a given learning object."""

        queryset = super().get_queryset()
        learning_type = self.request.query_params.get("learning_type")
        learning_obj_id = self.request.query_params.get(learning_type)
        if not learning_obj_id:
            return queryset.none()
        filter_params = {
            f"related_enrollments__{learning_type}": learning_obj_id,
            "related_enrollments__is_enrolled": True,
        }
        users = list(User.objects.filter(**filter_params).values_list("id", flat=True))
        user_group_members = list(UserGroup.objects.filter(**filter_params).values_list("members", flat=True))
        return queryset.filter(id__in=users + user_group_members)


class EnrollmentBulkUploadAPIView(AppAPIView):
    """API View to upload Bulk Enrollment from xlsx file"""

    def post(self, request, *args, **kwargs):
        """Handle on post"""

        if not (uploaded_file := request.FILES.get("file")):
            return self.send_error_response(data="File not found")
        if not uploaded_file.name.endswith(".xlsx"):
            return self.send_error_response(data="Unsupported file format. Please upload a .xlsx file.")
        db_name = get_current_db_name()
        folder_path = f"apps/media/temp/{db_name}/enrollment_bulk_upload"
        file_path = process_and_save_uploaded_file(uploaded_file, folder_path)
        EnrollmentBulkUploadTask().run_task(
            file_path=file_path,
            db_name=db_name,
            authenticated_user=self.get_user().id,
            request={"headers": dict(request.headers)},
        )
        return self.send_response(data={"message": "Enrollment Bulk Upload Successfull"})


class EnrollmentBulkUploadSampleFileAPIView(AppAPIView):
    """API to generate a sample xlsx file for Enrollment Bulk Upload"""

    def get(self, request, *args, **kwargs):
        """Handle on GET"""

        buffer = BytesIO()
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Enrollment_Bulk_Upload"

        data = (
            ["TenantName", "UserEmail", "Type", "TypeName", "Code", "EndDate"],
            ["testpro", "user@example.com", "course", "python", "ASS_ERT_01", "mm/dd/yyyy"],
            ["testpro", "user@example.com", "learning_path", "python", "LP_09_E3", "mm/dd/yyyy"],
            ["testpro", "user@example.com", "advanced_learning_path", "python", "ALP_K_99", "mm/dd/yyyy"],
            ["testpro", "user@example.com", "skill_traveller", "python", "SK_TR_09", "mm/dd/yyyy"],
            ["testpro", "user@example.com", "playground", "python", "PG_ER_3S", "mm/dd/yyyy"],
            ["testpro", "user@example.com", "playground_group", "python", "PGG_ER_3T", "mm/dd/yyyy"],
        )
        for row in data:
            worksheet.append(row)
        workbook.save(buffer)
        buffer.seek(0)
        response = Response(
            headers={"Content-Disposition": "attachment; filename=Enrollment_Bulk_Upload_Template.xlsx"},
            content_type="application/ms-excel",
        )
        response.content = buffer.read()
        return response


class UnenrollmentBulkUploadAPIView(AppAPIView):
    """API View to Unenroll Bulk Users"""

    def post(self, request, *args, **kwargs):
        """Handle on Post"""

        if not (uploaded_file := request.FILES.get("file")):
            return self.send_error_response(data="File not found")
        if not uploaded_file.name.endswith(".xlsx"):
            return self.send_error_response(data="Unsupported file format. Please upload a .xlsx file.")
        db_name = get_current_db_name()
        folder_path = f"apps/media/temp/{db_name}/unenrollment_bulk_upload"
        file_path = process_and_save_uploaded_file(uploaded_file, folder_path)
        BulkUnenrollmentTask().run_task(file_path=file_path, db_name=db_name)
        return self.send_response()


class UnenrollmentBulkUploadSampleFileAPIView(AppAPIView):
    """API to generate a sample xlsx file for UnEnrollment Bulk Upload"""

    def get(self, request, *args, **kwargs):
        """Handle on GET"""

        buffer = BytesIO()
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Unenrollment_Bulk_Upload"

        data = (
            ["UserEmail", "Type", "Code"],
            ["user@example.com", "course", "ASS_ERT_01"],
            ["user@example.com", "learning_path", "LP_09_E3"],
            ["user@example.com", "advanced_learning_path", "ALP_K_99"],
            ["user@example.com", "skill_traveller", "SK_TR_09"],
            ["user@example.com", "playground", "PG_ER_3S"],
            ["user@example.com", "playground_group", "PGG_ER_3T"],
        )
        for row in data:
            worksheet.append(row)
        workbook.save(buffer)
        buffer.seek(0)
        response = Response(
            headers={"Content-Disposition": "attachment; filename=UnEnrollment_Bulk_Upload_Template.xlsx"},
            content_type="application/ms-excel",
        )
        response.content = buffer.read()
        return response


class EnrollmentReminderCUDApiViewSet(AppModelCUDAPIViewSet):
    """ViewSet for create, update & destroy Enrollment Reminder."""

    serializer_class = EnrollmentReminderCUDModelSerializer
    queryset = EnrollmentReminder.objects.all()


class EnrollmentReminderListApiViewSet(AppModelListAPIViewSet):
    """ViewSet to list Enrollment Reminders."""

    serializer_class = EnrollmentReminderListModelSerializer
    queryset = EnrollmentReminder.objects.all()
    search_fields = ["learning_type"]
