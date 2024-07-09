from datetime import datetime

from apps.access.helpers import idp_user_onboard
from apps.access.tasks import AutoAssignLearningTask
from apps.common.idp_service import idp_admin_auth_token
from apps.common.tasks import BaseAppTask
from apps.tenant_service.middlewares import get_current_tenant_details


class UserBulkUploadTask(BaseAppTask):
    """Task to Bulk Upload the Users"""

    def run(self, list_of_users, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User, UserDetail, UserSkillDetail
        from apps.access_control.models import UserGroup, UserRole
        from apps.learning.config import ProficiencyChoices
        from apps.learning.models import CategorySkill
        from apps.meta.models import (
            City,
            Country,
            DepartmentCode,
            DepartmentTitle,
            EmploymentStatus,
            JobDescription,
            JobTitle,
            State,
        )

        self.switch_db(db_name)
        self.logger.info("Executing UserBulkUploadTask.")
        auth_token = idp_admin_auth_token()
        tenant_details = get_current_tenant_details()
        tenant_data = {
            "idp_id": tenant_details["idp_id"],
            "name": tenant_details["name"],
            "tenancy_name": tenant_details["tenancy_name"],
            "issuer_url": tenant_details.get("issuer_url"),
        }
        if not tenant_details["is_unlimited_users_allowed"]:
            limit = tenant_details["allowed_user_count"] - User.objects.all().count()
            list_of_users = list_of_users[:limit]
        for user_data in list_of_users:
            if (
                not user_data["Email"]
                or not user_data["Tenant Name"]
                or not user_data["Role"]
                or not user_data["First Name"]
            ):
                continue
            if user_data.get("Employee Id"):
                unique_id = UserDetail.objects.filter(employee_id=user_data["Employee Id"]).exists()
                if unique_id:
                    user_data["Employee Id"] = None
            if user_data.get("User Id Number"):
                unique_id = UserDetail.objects.filter(user_id_number=user_data["User Id Number"]).exists()
                if unique_id:
                    user_data["User Id Number"] = None
            role_list = user_data.get("Role").split(",")
            roles = []
            for role in role_list:
                user_role = UserRole.objects.filter(name__icontains=role.strip()).first()
                if user_role:
                    roles.append(user_role.id)
            user = {
                "first_name": user_data["First Name"],
                "last_name": user_data["Last Name"],
                "email": user_data["Email"],
                "is_active": user_data.get("Active") or True,
            }
            user_instance, created = User.objects.update_or_create(username=user_data["Email"], defaults=user)
            if created:
                user_instance.roles.set(roles)
                employment_status = (
                    EmploymentStatus.objects.get_or_create(name=user_data["Employment Status"])[0]
                    if user_data.get("Employment Status")
                    else None
                )
                job_description = (
                    JobDescription.objects.get_or_create(name=user_data["Job Description"])[0]
                    if user_data.get("Job Description")
                    else None
                )
                job_title = (
                    JobTitle.objects.get_or_create(name=user_data["Job Title"])[0]
                    if user_data.get("Job Title")
                    else None
                )
                department_code = (
                    DepartmentCode.objects.get_or_create(name=user_data["Department Code"])[0]
                    if user_data.get("Department Code")
                    else None
                )
                department_title = (
                    DepartmentTitle.objects.get_or_create(name=user_data["Department Title"])[0]
                    if user_data.get("Department Title")
                    else None
                )
                country = state = city = None
                if user_data.get("Country"):
                    country = Country.objects.get_or_create(name=user_data["Country"])[0]
                if country and user_data.get("State"):
                    state = State.objects.get_or_create(name=user_data["State"], country=country)[0]
                if state and user_data.get("City"):
                    city = City.objects.get_or_create(name=user_data["City"], state=state)[0]
                user_details = self.get_user_details_data(
                    user_data=user_data,
                    job_description=job_description,
                    job_title=job_title,
                    department_code=department_code,
                    department_title=department_title,
                    employment_status=employment_status,
                    city=city,
                    state=state,
                    country=country,
                )
                user_detail, created = UserDetail.objects.update_or_create(user=user_instance, defaults=user_details)
                if user_data.get("Skill"):
                    skill_list = user_data.get("Skill").split(",")
                    skills = []
                    for skill in skill_list:
                        category_skill, created = CategorySkill.objects.get_or_create(name=skill.strip())
                        if category_skill:
                            user_skill, created = UserSkillDetail.objects.get_or_create(
                                skill=category_skill, proficiency=ProficiencyChoices.basic
                            )
                            skills.append(user_skill.id)
                    user_detail.skill_detail.set(skills)
                if user_data.get("Business Unit/User Group"):
                    user_group = UserGroup.objects.filter(name=user_data["Business Unit/User Group"].strip()).first()
                    if user_group:
                        user_group.members.add(user_instance)
                success, message = idp_user_onboard(user_instance, tenant_data, auth_token)
                if not success:
                    user_instance.is_active = False
                    user_instance.save()
                    continue
                if tenant_details["idp_id"] == 482:
                    AutoAssignLearningTask().run_task(user_id=user_instance.id, db_name=db_name)
        return True

    @staticmethod
    def get_user_details_data(**kwargs):
        """Initial User Detail Data."""

        user_data = kwargs["user_data"]
        if user_data.get("Start Date") and not isinstance(user_data["Start Date"], datetime):
            user_data["Start Date"] = datetime.strptime(user_data["Start Date"], "%m/%d/%Y")
        return {
            "user_id_number": user_data.get("User Id Number"),
            "user_grade": user_data.get("User Grade"),
            "manager_name": user_data.get("Current Manager Name"),
            "manager_email": user_data.get("Current Manager Email"),
            "business_unit_name": user_data.get("Business Unit/User Group"),
            "manager_id": user_data.get("Current Manager Employee Id"),
            "config_str": user_data.get("Config Json"),
            "employment_start_date": user_data.get("Start Date"),
            "employee_id": user_data.get("Employee Id"),
            "manager_two_email": user_data.get("Manager 2 Email"),
            "manager_three_email": user_data.get("Manager 3 Email"),
            "job_description": kwargs["job_description"],
            "job_title": kwargs["job_title"],
            "department_code": kwargs["department_code"],
            "department_title": kwargs["department_title"],
            "employment_status": kwargs["employment_status"],
            "current_city": kwargs["city"],
            "current_state": kwargs["state"],
            "current_country": kwargs["country"],
            "is_onsite_user": user_data.get("Is Onsite User") or False,
        }
