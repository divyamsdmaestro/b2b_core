from datetime import datetime, timedelta

from django.conf import settings

from apps.common.communicator import get_request
from apps.tenant_service.middlewares import get_current_tenant_idp_id


def get_virtutor_roles_by_tenant(auth_token):
    """Returns the list of roles by tenant."""

    success, data = get_request(
        service="VIRTUTOR",
        url_path=settings.VIRTUTOR_CONFIG["get_roles_by_tenant_url"],
        params={"tenantId": get_current_tenant_idp_id()},
        auth_token=auth_token,
    )
    if success and not data or not data.get("result", None):
        return False, {"error": "Failed to fetch roles by tenant."}
    return success, data


def get_virtutor_trainer_details(auth_token, trainer_id):
    """Returns the details of trainer."""

    success, data = get_request(
        service="VIRTUTOR",
        url_path=settings.VIRTUTOR_CONFIG["get_trainer_details_url"],
        params={"mentorIds": trainer_id},
        auth_token=auth_token,
    )
    error_message = {"error": "Failed to fetch trainer details."}
    if success and not data.get("result"):
        return False, error_message
    elif success and data["result"] and not data["result"].get("irisTrainerRecordDetails"):
        return False, error_message
    return success, data


def get_virtutor_session_details(auth_token, scheduled_id):
    """Returns the details of session."""

    success, data = get_request(
        service="VIRTUTOR",
        url_path=settings.VIRTUTOR_CONFIG["get_particular_session_url"],
        params={"sessionScheduleId": scheduled_id},
        auth_token=auth_token,
    )
    if success and not data.get("result"):
        return False, {"error": "Failed to fetch session details."}
    return success, data


def get_virtutor_session_participant_list(auth_token, scheduled_id, session_code):
    """Returns the participants list of a session."""

    success, data = get_request(
        service="VIRTUTOR",
        url_path=settings.VIRTUTOR_CONFIG["get_all_session_participants_url"],
        params={"sessionScheduleId": scheduled_id, "sessionCode": session_code},
        auth_token=auth_token,
    )
    if success and not data.get("result"):
        return False, {"error": "Failed to fetch session participants list."}
    return success, data


def get_session_recordings_url(auth_token, scheduled_id, session_code):
    """Returns the recorded session urls."""

    success, data = get_request(
        service="VIRTUTOR",
        url_path=settings.VIRTUTOR_CONFIG["get_session_recordings_url"],
        params={"sessionScheduleId": scheduled_id, "sessionCode": session_code},
        auth_token=auth_token,
    )
    if success and not data:
        return False, {"error": "Failed to fetch recordings."}
    return success, data


def format_datetime(datetime):
    """Function to format the date and time."""

    return datetime.strftime("%m/%d/%Y %I:%M %p")


def convert_utc_to_ist(utc_datetime_str):
    """
    Convert UTC-formatted datetime string to Indian Standard Time (IST).
    """

    return datetime.fromisoformat(utc_datetime_str) + timedelta(hours=5, minutes=30)
