from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.access.models import User, UserDetail
from apps.access.serializers.v1 import (
    AdminProfileUpdateSerializer,
    UserAreaOfInterestUpdateSerializer,
    UserProfileUpdateSerializer,
)
from apps.access_control.models import UserGroup, UserRole
from apps.common.helpers import unpack_dj_choices
from apps.common.idp_service import idp_admin_auth_token, idp_post_request
from apps.common.serializers import (
    AppSerializer,
    AppSpecificImageFieldSerializer,
    BaseIDNameSerializer,
    get_app_read_only_serializer,
)
from apps.common.views.api import AppAPIView
from apps.learning.config import ProficiencyChoices
from apps.learning.models import Category, CategoryRole, CategorySkill
from apps.tenant_service.middlewares import get_current_tenant_name
from config.settings import IDP_CONFIG


class AdminProfileUpdateAPIView(AppAPIView):
    """View to handle admin `Profile` update."""

    serializer_class = AdminProfileUpdateSerializer

    def get(self, request, *args, **kwargs):
        """Returns the meta data for update."""

        return self.send_response(data=self.serializer_class(instance=self.get_user()).get_meta_for_update())

    def post(self, request, *args, **kwargs):
        """Update `User` model details for the current admin."""

        serializer = self.get_valid_serializer(instance=self.get_user())
        serializer.save()
        return self.send_response(data=serializer.data)


class AdminUserDeboardOrLoginDeleteAPIView(AppAPIView):
    """Tenant Admin to perform other user profile update or delete."""

    class _Serializer(AppSerializer):
        """`User` update or delete serializer for Tenant Admin."""

        users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
        is_login_restrict = serializers.BooleanField(default=False)
        is_deboard = serializers.BooleanField(default=False)
        is_allow_login = serializers.BooleanField(default=False)

        def validate(self, attrs):
            """Validate if either `is_login_restrict` or `is_deboard` should be given."""

            if not attrs.get("is_login_restrict") and not attrs.get("is_deboard") and not attrs.get("is_allow_login"):
                raise serializers.ValidationError({"users": "Required Action to perform is not selected"})
            return attrs

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Update `User` based on actions for Tenant Admin."""

        validated_data = self.get_valid_serializer().validated_data
        users_id_list = request.data["users"]  # just to get all the ids instead of objects. Need to change later.
        if validated_data.get("is_login_restrict"):
            User.objects.filter(id__in=users_id_list).update(is_active=False)
        if validated_data.get("is_deboard"):
            User.objects.filter(id__in=users_id_list).hard_delete()
        if validated_data.get("is_allow_login"):
            User.objects.filter(id__in=users_id_list).update(is_active=True)
        return self.send_response(data="Action performed successfully.")


class AdminUserRoleUpdateAPIView(AppAPIView):
    """Admin to perform other user update."""

    class _Serializer(AppSerializer):
        """`User` update or delete serializer for Tenant Admin."""

        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        roles = serializers.PrimaryKeyRelatedField(queryset=UserRole.objects.all(), many=True)

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Update `User` based on actions for Tenant Admin."""

        validated_data = self.get_valid_serializer().validated_data
        to_user = validated_data["user"]
        roles = validated_data["roles"]
        to_user.roles.set(roles)
        to_user.current_role = None
        to_user.save()
        return self.send_response(data="Action performed successfully.")


class AdminUserGroupUpdateAPIView(AppAPIView):
    """Admin to perform other user group update."""

    class _Serializer(AppSerializer):
        """`User` update or delete serializer for Tenant Admin."""

        users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
        groups = serializers.PrimaryKeyRelatedField(queryset=UserGroup.objects.all(), many=True)

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Update `User` based on actions for Tenant Admin."""

        validated_data = self.get_valid_serializer().validated_data
        users = validated_data["users"]
        groups = validated_data["groups"]
        for group in groups:
            group.members.add(*users)
            group.save()
        return self.send_response(data="Action performed successfully.")


class AdminUserPasswordUpdateAPIView(AppAPIView):
    """Tenant Admin to perform other user password update."""

    class _Serializer(AppSerializer):
        """Serializer for the same."""

        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        password = serializers.CharField(min_length=8, max_length=32)
        confirm_password = serializers.CharField(min_length=8, max_length=32)

        def validate_password(self, password):
            """Validate password."""

            password_validation.validate_password(password=password)
            return password

        def validate(self, attrs):
            """Validate password & confirm password."""

            if attrs["password"] != attrs["confirm_password"]:
                raise serializers.ValidationError({"password": "Passwords do not match."})
            return attrs

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Handle in post."""

        validated_data = self.get_valid_serializer().validated_data
        user = validated_data["user"]
        password = validated_data["password"]
        auth_token = idp_admin_auth_token(raise_drf_error=True, field="password")
        success, admin_data = idp_post_request(
            url_path=IDP_CONFIG["external_reset_password_url"],
            auth_token=auth_token,
            data={
                "userName": user.email,
                "tenantName": get_current_tenant_name(),
                "newPassword": password,
            },
        )
        if not success:
            raise serializers.ValidationError({"password": "IDP Admin Password set failed."})
        user.password = make_password(password)
        user.save()
        return self.send_response(data=f"Password updated successfully for user {user.name} ({user.email}).")


class UserProfileUpdateAPIView(AppAPIView):
    """View to handle Learner `Profile` update."""

    serializer_class = UserProfileUpdateSerializer

    def get(self, request, *args, **kwargs):
        """Returns the meta data for update."""

        return self.send_response(data=self.serializer_class(instance=self.get_user()).get_meta_for_update())

    def post(self, request, *args, **kwargs):
        """Update `User` model details for the current user."""

        serializer = self.get_valid_serializer(instance=self.get_user())
        serializer.save()
        return self.send_response(data=serializer.data)


class UserRoleSwitchAPIView(AppAPIView):
    """View to handle role switch."""

    class _Serializer(AppSerializer):
        """Serializer for the view."""

        role = serializers.PrimaryKeyRelatedField(queryset=UserRole.objects.all())

        def validate_role(self, role):
            """Validate if the role exists in user roles."""

            user = self.get_user()
            if role not in user.roles.all():
                raise serializers.ValidationError("Invalid role.")
            return role

    serializer_class = _Serializer

    def get(self, request, *args, **kwargs):
        """Returns the meta data for update."""

        return self.send_response(data=BaseIDNameSerializer(self.get_user().roles.all(), many=True).data)

    def post(self, request, *args, **kwargs):
        """Switch the roles for the user."""

        user = self.get_user()
        validated_data = self.get_valid_serializer().validated_data
        role = validated_data["role"]
        user.current_role = role
        user.save()
        return self.send_response(data={"active_role_type": role.role_type})


class UserAreaOfInterestUpdateAPIView(AppAPIView):
    """Api view to update the area of interest in user detail model."""

    serializer_class = UserAreaOfInterestUpdateSerializer

    def post(self, request, *args, **kwargs):
        """Update category, role & skill detail for the current user."""

        user = self.get_user()
        user_detail_obj, created = UserDetail.objects.get_or_create(user=user)
        serializer = self.get_valid_serializer(instance=user_detail_obj)
        skill_detail_data = serializer.validated_data.pop("skill_detail", [])
        instance = serializer.save()
        for skill_detail in skill_detail_data:
            instance.skill_detail.update_or_create(**skill_detail)
        user.data["is_area_of_interest_given"] = True
        user.save()
        return self.send_response(data={"message": "Area of interest added successfully."})


class UserAreaOfInterestUpdateMetaAPIView(AppAPIView):
    """Meta Api view to update the area of interest."""

    def get(self, *args, **kwargs):
        """Returns the meta data."""

        return self.send_response(
            data={
                "skill": get_app_read_only_serializer(
                    meta_model=CategorySkill,
                    meta_fields=["id", "name", "image", "description"],
                    init_fields_config={"image": AppSpecificImageFieldSerializer()},
                )(CategorySkill.objects.alive(), many=True).data,
                "role": get_app_read_only_serializer(
                    meta_model=CategoryRole,
                    meta_fields=["id", "name"],
                )(CategoryRole.objects.alive(), many=True).data,
                "category": get_app_read_only_serializer(
                    meta_model=Category,
                    meta_fields=["id", "name"],
                )(Category.objects.alive(), many=True).data,
                "proficiency": unpack_dj_choices(ProficiencyChoices.choices),
            }
        )
