from apps.access.models import User
from apps.access_control.models import UserRole
from apps.common.idp_service import idp_admin_auth_token
from apps.common.views.api import AppAPIView, NonAuthenticatedAPIMixin
from apps.learning.communicator import chat_post_request
from apps.techademy_one.v1.serializers import T1UserOnboardSerializer
from apps.tenant_service.middlewares import set_db_for_router
from config.settings import CHAT_CONFIG


class T1UserOnboardAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to create User."""

    serializer_class = T1UserOnboardSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        # TODO: Authentication, super admin details integration.
        validated_data = self.get_valid_serializer().validated_data
        if validated_data.pop("is_already_exists", None):
            return self.send_response(
                data={
                    "user_id": validated_data["user_obj"].uuid,
                    "message": "User already created.",
                }
            )
        tenant_obj = validated_data.pop("tenant_obj")
        set_db_for_router(tenant_obj.db_name)
        role_names = validated_data["group_details"]
        roles = []
        for role_name in role_names:
            try:
                roles.append(UserRole.objects.get(name=role_name))
            except Exception:
                pass
        try:
            user = User.objects.create_user(
                uuid=validated_data["user_id"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                email=validated_data["email"],
            )
            user.roles.add(*roles)
        except Exception:
            return self.send_error_response(data={"message": "Something went wrong while onboarding user."})
        try:
            chat_user_data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "user_id": user.uuid,
                "tenant": {"tenant_id": tenant_obj.uuid, "name": tenant_obj.tenantcy_name},
            }
            chat_request_headers = {"Token": idp_admin_auth_token()}
            chat_post_request(
                url_path=CHAT_CONFIG["user_onboard_url"], data=chat_user_data, headers=chat_request_headers
            )
        except Exception:
            pass
        return self.send_response(data={"message": "User Onboarded Successfully."})
