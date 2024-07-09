from apps.access.helpers import idp_user_onboard
from apps.common.tasks import BaseAppTask
from apps.tenant_service.middlewares import get_current_tenant_details
from config.settings import CHAT_CONFIG


class T1BulkUserOnboardTask(BaseAppTask):
    """Task to Bulk On-board User from Techademy One."""

    def run(self, tenant_id, user_details):
        """Run handler."""

        from apps.access.models import User
        from apps.access_control.config import RoleTypeChoices
        from apps.access_control.models import UserRole
        from apps.common.idp_service import idp_admin_auth_token
        from apps.learning.communicator import chat_post_request
        from apps.tenant.models import Tenant

        self.switch_db()
        tenant: Tenant = Tenant.objects.get(id=tenant_id)
        self.logger.info(f"Got T1BulkUserOnboardTask for Tenant - {tenant.name}.")
        tenant_details = get_current_tenant_details()
        auth_token = idp_admin_auth_token()  # TODO: Need to clarify with jeevan why user is onboarded in IDP.
        tenant_data = {
            "idp_id": tenant_details["idp_id"],
            "name": tenant_details["name"],
            "tenancy_name": tenant_details["tenancy_name"],
            "issuer_url": tenant_details.get("issuer_url"),
        }
        self.switch_db(db_name=tenant.db_name)
        learner = UserRole.objects.filter(role_type=RoleTypeChoices.learner).order_by("created_at").first()
        for user_detail in user_details:
            try:
                user = User.objects.create_user(
                    uuid=user_detail["user_id"],
                    first_name=user_detail["first_name"],
                    last_name=user_detail["last_name"],
                    email=user_detail["email"],
                )
                user.roles.add(learner)
                success, message = idp_user_onboard(user, tenant_data, auth_token)
                if not success:
                    user.is_active = False
                    user.save()
                try:
                    chat_user_data = {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "user_id": user.uuid,
                        "tenant": {"tenant_id": tenant_details["idp_id"], "name": tenant_details["tenantcy_name"]},
                    }
                    chat_request_headers = {"Token": auth_token()}
                    chat_post_request(
                        url_path=CHAT_CONFIG["user_onboard_url"], data=chat_user_data, headers=chat_request_headers
                    )
                except Exception:
                    pass
            except Exception:
                pass
        return True
