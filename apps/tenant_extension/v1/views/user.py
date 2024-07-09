""""
Note:
    If more tenant requests for custom user onboard API then make sub-folders based on tenant name
    and add custom views instead of this common view.
"""
from apps.access.helpers import idp_user_onboard
from apps.access.models import User, UserDetail
from apps.access_control.config import RoleTypeChoices
from apps.access_control.models import UserRole
from apps.common.views.api import AppAPIView
from apps.meta.models import DepartmentCode, DepartmentTitle, EmploymentStatus, JobDescription, JobTitle
from apps.tenant_extension.v1.serializers import (
    CustomUserOnboardSerializer,
    CustomUserStatusSerializer,
    CustomUserUpdateSerializer,
)


class CustomUserOnboardAPIView(AppAPIView):
    """Api view to create User. Primarily for Prolifics tenant."""

    serializer_class = CustomUserOnboardSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        validated_data = self.get_valid_serializer().validated_data
        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        if learner_role := UserRole.objects.filter(role_type=RoleTypeChoices.learner).order_by("created_at").first():
            user.roles.add(learner_role)
        user_details_data = validated_data["user_details"]
        user_details, created = UserDetail.objects.update_or_create(
            user=user,
            user_id_number=validated_data["user_id_number"],
            defaults={
                "user_grade": user_details_data.get("user_grade"),
                "employment_start_date": user_details_data.get("employment_start_date"),
                "manager_id": user_details_data.get("manager_id"),
                "manager_name": user_details_data.get("manager_name"),
                "manager_email": user_details_data.get("manager_email"),
                "manager_two_email": user_details_data.get("manager_two_email"),
                "manager_three_email": user_details_data.get("manager_three_email"),
                "business_unit_name": user_details_data.get("business_unit_name"),
                "is_onsite_user": user_details_data.get("is_onsite_user"),
            },
        )
        if job_description := user_details_data.get("job_description"):
            jd_instance, created = JobDescription.objects.get_or_create(name=job_description)
            user_details.job_description = jd_instance
        if job_title := user_details_data.get("job_title"):
            jt_instance, created = JobTitle.objects.get_or_create(name=job_title)
            user_details.job_title = jt_instance
        if department_code := user_details_data.get("department_code"):
            dc_instance, created = DepartmentCode.objects.get_or_create(name=department_code)
            user_details.department_code = dc_instance
        if department_title := user_details_data.get("department_title"):
            dt_instance, created = DepartmentTitle.objects.get_or_create(name=department_title)
            user_details.department_title = dt_instance
        if employment_status := user_details_data.get("employment_status"):
            es_instance, created = EmploymentStatus.objects.get_or_create(name=employment_status)
            user_details.employment_status = es_instance
        user_details.save()
        success, message = idp_user_onboard(user)
        if not success:
            return self.send_error_response(data={"message": message})
        return self.send_response(data={"message": "User Onboarded Successfully."})


class CustomUserStatusAPIView(AppAPIView):
    """Api view to toggle User account status. Primarily for Prolifics tenant."""

    serializer_class = CustomUserStatusSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        validated_data = self.get_valid_serializer().validated_data
        user = validated_data["user"]
        if user.is_active != validated_data["is_active"]:
            user.is_active = validated_data["is_active"]
            user.save()
        return self.send_response(data={"message": "User Status Updated."})


class CustomUserUpdateAPIView(AppAPIView):
    """Api view to update User. Primarily for Prolifics tenant."""

    serializer_class = CustomUserUpdateSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        validated_data = self.get_valid_serializer().validated_data
        user = validated_data["user"]
        user.first_name = validated_data.get("first_name") or user.first_name
        user.last_name = validated_data.get("last_name") or user.last_name
        user.save()
        user_detail = user.user_detail
        user_details = validated_data.pop("user_details")
        user_detail.user_id_number = user_details.get("user_id_number") or user_detail.user_id_number
        user_detail.user_grade = user_details.get("user_grade") or user_detail.user_grade
        user_detail.employee_id = user_details.get("employee_id") or user_detail.employee_id
        user_detail.employment_start_date = (
            user_details.get("employment_start_date") or user_detail.employment_start_date
        )
        user_detail.manager_id = user_details.get("manager_id") or user_detail.manager_id
        user_detail.manager_name = user_details.get("manager_name", user_detail.manager_name)
        user_detail.manager_email = user_details.get("manager_email", user_detail.manager_email)
        user_detail.manager_two_email = user_details.get("manager_two_email") or user_detail.manager_two_email
        user_detail.manager_three_email = user_details.get("manager_three_email") or user_detail.manager_three_email
        user_detail.business_unit_name = user_details.get("business_unit_name") or user_detail.business_unit_name
        user_detail.is_onsite_user = user_details.get("is_onsite_user") or user_detail.is_onsite_user

        if job_description := user_details.get("job_description"):
            jd_instance, created = JobDescription.objects.get_or_create(name=job_description)
            user_detail.job_description = jd_instance
        if job_title := user_details.get("job_title"):
            jt_instance, created = JobTitle.objects.get_or_create(name=job_title)
            user_detail.job_title = jt_instance
        if department_code := user_details.get("department_code"):
            dc_instance, created = DepartmentCode.objects.get_or_create(name=department_code)
            user_detail.department_code = dc_instance
        if department_title := user_details.get("department_title"):
            dt_instance, created = DepartmentTitle.objects.get_or_create(name=department_title)
            user_detail.department_title = dt_instance
        if employment_status := user_details.get("employment_status"):
            es_instance, created = EmploymentStatus.objects.get_or_create(name=employment_status)
            user_detail.employment_status = es_instance
        user_detail.save()
        return self.send_response(data={"message": "User Details Updated."})
