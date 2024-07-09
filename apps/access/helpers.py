from django.contrib.auth.hashers import make_password

from apps.access.tasks import UserOnboardEmailTask
from apps.common.idp_service import idp_admin_auth_token, idp_post_request
from apps.learning.communicator import chat_post_request
from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_details
from config.settings import CHAT_CONFIG, IDP_CONFIG


def idp_user_onboard(user, tenant_data=None, auth_token=None):
    """Onboard the user on IDP."""

    if not tenant_data:
        tenant_data = get_current_tenant_details()
    if not auth_token:
        auth_token = idp_admin_auth_token()
    user_data = user.get_user_init_data_idp()
    payload = {
        "userId": 0,
        "tenantId": tenant_data["idp_id"],
        "tenantDisplayName": tenant_data["name"],
        "tenantName": tenant_data["tenancy_name"],
        "role": user_data["role"],
        "email": user_data["email"],
        "name": user_data["name"],
        "surname": user_data["surname"],
        "configJson": "string",
        "password": user_data["password"],
        "businessUnitName": user_data["businessUnitName"],
        "userIdNumber": user_data["userIdNumber"],
        "userGrade": "string",
        "isOnsiteUser": "string",
        "managerName": user_data["managerName"],
        "managerEmail": user_data["managerEmail"],
        "managerId": 0,
        "organizationUnitId": 0,
    }
    success, data = idp_post_request(
        url_path=IDP_CONFIG["get_or_onboard_user_url"], data=payload, auth_token=auth_token
    )
    message = None
    if not success:
        message = "User IDP Registration Failed!"
    user.idp_id = data["userId"]
    user.password = make_password(user_data["password"])
    user.save()
    try:
        chat_user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "user_id": user.idp_id,
            "tenant": {"tenant_id": tenant_data["idp_id"], "name": tenant_data["tenancy_name"]},
        }
        chat_request_headers = {"Token": auth_token}
        chat_post_request(url_path=CHAT_CONFIG["user_onboard_url"], data=chat_user_data, headers=chat_request_headers)
    except Exception:
        pass
    UserOnboardEmailTask().run_task(user_id=user.id, password=user_data["password"], db_name=get_current_db_name())
    return True, message
