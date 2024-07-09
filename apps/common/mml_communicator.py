import requests
from django.conf import settings

from apps.tenant_service.middlewares import get_current_tenant_details, get_current_tenant_mml_id


def mml_vm_creation(idp_token, mml_sku_id, vm_name, kc_flag=None):
    """Creates the vm for mml."""

    # MML AUTHENTICATION REQUEST
    mml_tenant_id = get_current_tenant_mml_id()
    if not mml_tenant_id:
        return False, "Labs not enabled. Contact administrator.", None

    tenant_details = get_current_tenant_details()
    mml_host = tenant_details.get("mml_host", None) or settings.MML_CONFIG["host"]
    mml_authentication_payload = {"token": idp_token, "tenant_id": str(mml_tenant_id)}
    mml_authentication = requests.post(
        url=f"{mml_host}{settings.MML_CONFIG['authenticate_url']}",
        json=mml_authentication_payload,
        verify=False,
    )
    if mml_authentication.status_code != 200 and mml_authentication.status_code == 400:
        return False, mml_authentication.json(), None
    elif mml_authentication.status_code == 500:
        return False, "Something went wrong. Contact us.", None
    mml_authenticated_user = mml_authentication.json().get("success", None)

    # No Role required for KC
    if kc_flag:
        mml_authentication_headers = {
            "Content-Type": "application/json",
            "Authorization": mml_authenticated_user.get("accessToken", None),
            "authType": mml_authenticated_user.get("auth_type", None),
            "tenant": mml_authenticated_user.get("localTenantId", None)
        }
    else:
        mml_authentication_headers = {
            "Content-Type": "application/json",
            "Authorization": mml_authenticated_user.get("accessToken", None),
            "authType": mml_authenticated_user.get("auth_type", None),
            "tenant": mml_authenticated_user.get("localTenantId", None),
            "role": mml_authenticated_user.get("role", None),
        }
    # MML VM CREATE REQUEST
    vm_request_payload = {"sku": str(mml_sku_id), "vm_name": vm_name, "status": 5}
    vm_create_request = requests.post(
        url=f"{mml_host}{settings.MML_CONFIG['vm_request_url']}",
        json=vm_request_payload,
        headers=mml_authentication_headers,
        verify=False,
    )
    mml_authentication_headers["mml_host"] = mml_host
    if vm_create_request.status_code == 201:
        return True, vm_create_request.json(), mml_authentication_headers
    elif vm_create_request.status_code != 200 and vm_create_request.json().get("type", None) != "Redirect":
        return False, vm_create_request.json(), None
    elif vm_create_request.status_code == 400 and vm_create_request.json().get("type", None) == "Redirect":
        return True, vm_create_request.json(), mml_authentication_headers
    else:
        return False, "Something went wrong. Contact us.", None
