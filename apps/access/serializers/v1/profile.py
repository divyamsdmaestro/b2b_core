from rest_framework import serializers

from apps.access.config import GenderChoices, MaritalStatusChoices
from apps.access.models import User, UserConnection, UserDetail, UserEducationDetail, UserSkillDetail
from apps.access.serializers.v1 import CommonUserDetailUpdateSerializer, CommonUserUpdateSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer
from apps.leaderboard.config import MilestoneChoices
from apps.leaderboard.tasks import CommonLeaderboardTask
from apps.learning.config import ProficiencyChoices
from apps.learning.models import CategoryRole, CategorySkill
from apps.meta.models import City, Country, EducationType, IdentificationType, State
from apps.tenant_service.middlewares import get_current_db_name


class UserEducationDetailCreateSerializer(AppWriteOnlyModelSerializer):
    """Handle serialization of Education Details."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserEducationDetail
        fields = ["education_type", "name", "university", "degree"]


class UserSkillDetailCreateSerializer(AppWriteOnlyModelSerializer):
    """Handle serialization of user skill details."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserSkillDetail
        fields = ["skill", "proficiency"]


class UserSkillDetailRetrieveSerializer(AppReadOnlyModelSerializer):
    """Serializer to retrieve user skill details."""

    skill = BaseIDNameSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserSkillDetail
        fields = ["skill", "proficiency"]


class AdminDetailUpdateSerializer(CommonUserDetailUpdateSerializer):
    """`UserDetail` model update serializer for Admin."""

    class Meta(CommonUserDetailUpdateSerializer.Meta):
        fields = CommonUserDetailUpdateSerializer.Meta.fields + [
            "permanent_address",
            "permanent_country",
            "permanent_state",
            "permanent_city",
            "permanent_pincode",
        ]


class AdminProfileUpdateSerializer(CommonUserUpdateSerializer):
    """`User` model update serializer for Admin."""

    user_details = AdminDetailUpdateSerializer()
    last_name = serializers.CharField(required=False)

    class Meta(CommonUserUpdateSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        """Overriden to update user details."""

        if user_details := validated_data.pop("user_details", None):
            user_detail_obj, created = UserDetail.objects.update_or_create(user=instance, defaults=user_details)

        return super().update(instance, validated_data)

    def get_meta_for_update(self, *args, **kwargs):
        """Overriden to add initial data of user details"""

        try:
            user_detail_obj = self.instance.related_user_details
        except User.related_user_details.RelatedObjectDoesNotExist:
            user_detail_obj = None
        data = super().get_meta_for_update()
        if user_detail_obj:
            data["initial"].update(
                {"user_details": AdminDetailUpdateSerializer(instance=user_detail_obj).get_meta_initial()}
            )
        return data

    def get_meta(self) -> dict:
        """get meta and initial values."""

        return {
            "gender": self.serialize_dj_choices(GenderChoices.choices),
            "current_country": self.serialize_for_meta(Country.objects.all(), fields=["id", "name"]),
            "current_state": self.serialize_for_meta(State.objects.all(), fields=["id", "name", "country"]),
            "current_city": self.serialize_for_meta(City.objects.all(), fields=["id", "name", "state"]),
            "permanent_country": self.serialize_for_meta(Country.objects.all(), fields=["id", "name"]),
            "permanent_state": self.serialize_for_meta(State.objects.all(), fields=["id", "name", "country"]),
            "permanent_city": self.serialize_for_meta(City.objects.all(), fields=["id", "name", "state"]),
        }


class UserDetailUpdateSerializer(CommonUserDetailUpdateSerializer):
    """`UserDetail` model update serializer for users."""

    education_detail = UserEducationDetailCreateSerializer(read_only=False, many=True)
    skill_detail = UserSkillDetailCreateSerializer(read_only=False, many=True)

    class Meta(CommonUserDetailUpdateSerializer.Meta):
        fields = CommonUserDetailUpdateSerializer.Meta.fields + [
            "marital_status",
            "identification_type",
            "identification_number",
            "role",
            "skill_detail",
            "education_detail",
        ]

    def get_meta_initial(self):
        """Overridden to update the field with serialized data."""

        initial_data = super().get_meta_initial()
        initial_data.update(
            {
                "skill_detail": self.serialize_for_meta(
                    queryset=self.instance.skill_detail.all(),
                    fields=[
                        "id",
                        "skill",
                        "proficiency",
                    ],
                ),
                "education_detail": self.serialize_for_meta(
                    queryset=self.instance.education_detail.all(),
                    fields=[
                        "id",
                        "education_type",
                        "name",
                        "university",
                        "degree",
                    ],
                ),
                "current_country": BaseIDNameSerializer(self.instance.current_country).data
                if self.instance.current_country
                else None,
                "current_state": BaseIDNameSerializer(self.instance.current_state).data
                if self.instance.current_state
                else None,
                "current_city": BaseIDNameSerializer(self.instance.current_city).data
                if self.instance.current_city
                else None,
                "employee_id": self.instance.employee_id,
                "employment_start_date": self.instance.employment_start_date,
                "manager_name": self.instance.manager_name,
                "manager_email": self.instance.manager_email,
                "manager_two_email": self.instance.manager_two_email,
                "manager_three_email": self.instance.manager_three_email,
                "job_title": BaseIDNameSerializer(self.instance.job_title).data if self.instance.job_title else None,
                "job_description": BaseIDNameSerializer(self.instance.job_description).data
                if self.instance.job_description
                else None,
                "department_code": BaseIDNameSerializer(self.instance.department_code).data
                if self.instance.department_code
                else None,
                "department_title": BaseIDNameSerializer(self.instance.department_title).data
                if self.instance.department_title
                else None,
                "employment_status": BaseIDNameSerializer(self.instance.employment_status).data
                if self.instance.employment_status
                else None,
            }
        )
        return initial_data


class UserProfileUpdateSerializer(CommonUserUpdateSerializer):
    """`User` model update serializer for users."""

    user_details = UserDetailUpdateSerializer(read_only=False)
    last_name = serializers.CharField(required=False)

    class Meta(CommonUserUpdateSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        """Overriden to update user details."""

        if user_details_data := validated_data.pop("user_details", None):
            education_details_data = user_details_data.pop("education_detail", [])
            skill_detail_data = user_details_data.pop("skill_detail", [])
            role_obj_list = user_details_data.pop("role", [])
            user_detail_obj, _ = UserDetail.objects.update_or_create(user=instance, defaults=user_details_data)
            user_detail_obj.role.set(role_obj_list)
            user_detail_obj.skill_detail.clear()
            user_detail_obj.education_detail.clear()
            skill_detail_objs = [UserSkillDetail.objects.get_or_create(**data)[0] for data in skill_detail_data]
            user_detail_obj.skill_detail.set(skill_detail_objs)
            education_detail_objs = [
                UserEducationDetail.objects.get_or_create(**data)[0] for data in education_details_data
            ]
            user_detail_obj.education_detail.set(education_detail_objs)
            fields = [
                "contact_number",
                "gender",
                "marital_status",
                "birth_date",
                "current_address",
                "current_city",
                "current_state",
                "current_country",
                "identification_number",
            ]
            if (
                all(getattr(user_detail_obj, field, None) is not None for field in fields)
                and user_detail_obj.education_detail.exists()
            ):
                CommonLeaderboardTask().run_task(
                    milestone_names=MilestoneChoices.profile_completion,
                    db_name=get_current_db_name(),
                    user_id=self.get_user().id,
                )
        return super().update(instance, validated_data)

    def get_meta_initial(self):
        """Overridden to update the user_details field value."""

        initial_data = super().get_meta_initial()
        user_connection_instance = UserConnection.objects.filter(user=self.instance).first()
        initial_data.update(
            {
                "friends": user_connection_instance.friends.count() if user_connection_instance else 0,
                "followers": user_connection_instance.followers.count() if user_connection_instance else 0,
                "following": User.objects.alive().filter(related_user_connections__followers=self.instance).count(),
            }
        )
        if user_detail_obj := UserDetail.objects.filter(user=self.instance).first():
            initial_data.update(
                {
                    "user_details": UserDetailUpdateSerializer(instance=user_detail_obj).get_meta_initial(),
                }
            )
        return initial_data

    def get_meta(self) -> dict:
        """get meta and initial values."""

        return {
            "gender": self.serialize_dj_choices(GenderChoices.choices),
            "marital_status": self.serialize_dj_choices(MaritalStatusChoices.choices),
            "proficiency": self.serialize_dj_choices(ProficiencyChoices.choices),
            "current_country": self.serialize_for_meta(Country.objects.all(), fields=["id", "name"]),
            "current_state": self.serialize_for_meta(State.objects.all(), fields=["id", "name", "country"]),
            "current_city": self.serialize_for_meta(City.objects.all(), fields=["id", "name", "state"]),
            "role": self.serialize_for_meta(CategoryRole.objects.alive(), fields=["id", "name"]),
            "skill": self.serialize_for_meta(CategorySkill.objects.alive(), fields=["id", "name"]),
            "identification_type": self.serialize_for_meta(IdentificationType.objects.all(), fields=["id", "name"]),
            "education_type": self.serialize_for_meta(EducationType.objects.all(), fields=["id", "name"]),
        }


class UserAreaOfInterestUpdateSerializer(AppWriteOnlyModelSerializer):
    """Serializer to update area of interests in user details."""

    skill_detail = UserSkillDetailCreateSerializer(many=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserDetail
        fields = [
            "category",
            "role",
            "skill_detail",
        ]
