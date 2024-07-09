from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from apps.access.models.user import User
from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer
from apps.access_control.config import RoleTypeChoices
from apps.access_control.models import UserGroup
from apps.common.communicator import post_request
from apps.common.serializers import AppSerializer
from apps.common.views.api import AppAPIView
from apps.event.config import CalendarEventTypeChoices
from apps.my_learning.models import Enrollment
from apps.my_learning.tasks import CalendarActivityCreationTask
from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_idp_id
from apps.virtutor.config import SessionJoinMechanismChoices
from apps.virtutor.helpers import (
    convert_utc_to_ist,
    format_datetime,
    get_session_recordings_url,
    get_virtutor_roles_by_tenant,
    get_virtutor_session_details,
    get_virtutor_session_participant_list,
    get_virtutor_trainer_details,
)
from apps.virtutor.models import ScheduledSession, Trainer
from apps.virtutor.serializers.v1 import SessionManagementSerializer, SessionScheduleSerializer


class ScheduleSessionApiView(AppAPIView):
    """
    Api view to schedule sessions in IIHT-VIRTUTOR.
    """

    serializer_class = SessionScheduleSerializer

    def get(self, request, *args, **kwargs):
        """Get the session join mechanism types."""

        data = self.serializer_class().serialize_dj_choices(SessionJoinMechanismChoices.choices)
        return self.send_response(data={"join_mechanism": data})

    def post(self, request, *args, **kwargs):
        """Schedule the sessions in IIHT-VIRTUTOR."""

        user = self.get_user()
        validated_data = self.get_valid_serializer().validated_data
        trainer_obj = validated_data["trainer"]
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        success, trainer_data = get_virtutor_trainer_details(auth_token=idp_token, trainer_id=trainer_obj.trainer_id)
        if not success:
            return self.send_error_response(trainer_data)
        trainer_details = trainer_data["result"]["irisTrainerRecordDetails"][0]
        success, role_data = get_virtutor_roles_by_tenant(auth_token=idp_token)
        if not success:
            return self.send_error_response(role_data)
        role_list = role_data["result"]
        mentor_role_id = next(role["roleId"] for role in role_list if role["roleName"] == "Mentor")
        mentee_role_id = next(role["roleId"] for role in role_list if role["roleName"] == "Mentee")
        mentor = {
            "isRemoved": False,
            "participantSessionRole": 1,  # Mentor(Trainer)
            "participantUserId": trainer_obj.trainer_id,
            "participantMoDRole": mentor_role_id,
            "participantName": trainer_details["name"],
            "participantSurname": trainer_details["surName"],
            "participantEmail": trainer_details["email"],
        }
        enrolled_users = self.get_enrolled_users(user, validated_data["module"])
        requested_mentee = []
        if user not in enrolled_users:
            requested_mentee.append(
                {
                    "isRemoved": False,
                    "participantSessionRole": 2,  # Mentee(Trainee)
                    "participantMoDRole": mentee_role_id,
                    "participantUserId": user.idp_id,
                    "participantName": user.first_name,
                    "participantSurname": user.last_name,
                    "participantEmail": user.email,
                }
            )
        participants = [mentor] + requested_mentee + self.get_mentee_data(enrolled_users, mentee_role_id)
        session_payload = self.get_session_payload(validated_data, user.idp_id, participants)
        # schedule the session.
        success, data = post_request(
            service="VIRTUTOR",
            url_path=settings.VIRTUTOR_CONFIG["create_session_url"],
            data=session_payload,
            auth_token=idp_token,
        )
        if success and not data["result"]["errorMessage"]:
            session, success = self.create_scheduled_session(validated_data, user, data)
            if enrolled_users:
                CalendarActivityCreationTask().run_task(
                    user_ids=list(enrolled_users.values_list("id", flat=True)),
                    event_type=CalendarEventTypeChoices.session,
                    event_instance_id=session.id,
                    db_name=get_current_db_name(),
                )
            return self.send_response(f"{session.session_title} scheduled successfully.")
        elif success and data["result"]["errorMessage"]:
            return self.send_error_response(
                data["result"]["errorMessage"]
                if data["result"]["errorMessage"]
                else "Something went wrong. Contact us."
            )
        else:
            return self.send_error_response("Something went wrong. Contact us.")

    def get_enrolled_users(self, user, module):
        """Returns a list of users enrolled in the given course's module."""

        if user.current_role and user.current_role.role_type in [RoleTypeChoices.admin, RoleTypeChoices.learner]:
            if user.current_role.role_type == RoleTypeChoices.learner:
                return User.objects.filter(id=user.id)
            elif user.current_role.role_type == RoleTypeChoices.admin:
                filter_params = {
                    "related_enrollments__course": module.course.id,
                    "related_enrollments__is_enrolled": True,
                }
                users = list(User.objects.filter(**filter_params).values_list("id", flat=True))
                user_group_members = list(UserGroup.objects.filter(**filter_params).values_list("members", flat=True))
                return User.objects.alive().filter(id__in=users + user_group_members, idp_id__isnull=False)
        return []

    def get_mentee_data(self, enrolled_users, mentee_role_id):
        """Returns the list of participants to scheduling a session."""

        return [
            {
                "isRemoved": False,
                "participantSessionRole": 2,  # Mentee(Trainee)
                "participantMoDRole": mentee_role_id,
                "participantUserId": enrolled_user.idp_id,
                "participantName": enrolled_user.first_name,
                "participantSurname": enrolled_user.last_name,
                "participantEmail": enrolled_user.email,
            }
            for enrolled_user in enrolled_users
        ]

    def get_session_payload(self, validated_data, user_idp_id, participants):
        """Returns the payload to scheduling the session for the given participants."""

        return {
            "startDate": format_datetime(validated_data["start_date"]),
            "endDate": format_datetime(validated_data["end_date"]),
            "joinMechanism": validated_data.get("join_mechanism", "1"),
            "recordingShelflifeDays": validated_data.get("recording_days") or 1,
            "requesterUserId": user_idp_id,
            "sessionAttributes": {"redirectUrl": "https://techademy.in/feedback/1"},
            "sessionStatus": 2,
            "sessionTitle": validated_data.get("session_title") or "Course Learner Session",
            "sessionType": 2,
            "skillIds": [],
            "tenantId": get_current_tenant_idp_id(),
            "timeZone": "India Standard Time",
            "participants": participants,
            "feedbackTemplateId": validated_data.get("feedback_template_id") or 0,
        }

    def create_scheduled_session(self, validated_data, user, data):
        """Create a new scheduled session in the current database for future use."""

        session_data = data["result"]
        session_args = {
            "session_title": validated_data["session_title"] if validated_data.get("session_title") else None,
            "session_code": session_data["sessionCode"],
            "scheduled_id": session_data["sessionScheduleId"],
            "session_url": session_data["sessionUrl"],
            "external_session_url": session_data["externalSessionUrl"],
            "base_url": session_data["virtutorBaseUrl"],
            "start_date": validated_data["start_date"],
            "end_date": validated_data["end_date"],
            "user": user,
            "creator_role": user.current_role.role_type if user.current_role else None,
        }
        session = validated_data["module"].related_scheduled_sessions.create(**session_args)
        return session, True


class SessionStartApiView(AppAPIView):
    """Api view to start a session."""

    def post(self, request, *args, **kwargs):
        """Function to start a session."""

        session = get_object_or_404(ScheduledSession, id=kwargs.get("pk"))
        user = self.get_user()
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        enrollment_instance = Enrollment.objects.filter(
            Q(user_group__in=user_groups) | Q(user=user), course=session.module.course
        ).first()
        if not enrollment_instance:
            return self.send_error_response("Session not found.")
        # Get particular session details using scheduled id.
        success, data = get_virtutor_session_details(auth_token=idp_token, scheduled_id=session.scheduled_id)
        if not success:
            return self.send_error_response(data)
        session_data = data["result"]
        start_time = convert_utc_to_ist(session_data["startDate"])
        end_time = convert_utc_to_ist(session_data["endDate"])
        current_time = datetime.now()
        if current_time > end_time:
            return self.send_error_response("Session has already ended.")
        elif current_time < start_time and (start_time - current_time).seconds > 300:
            return self.send_error_response(
                f"Session join link will be opened 5 minutes prior to the {format_datetime(start_time)}"
            )
        else:
            # start the session using session code.
            start_success, start_data = post_request(
                service="VIRTUTOR",
                url_path=settings.VIRTUTOR_CONFIG["start_session_url"],
                data={"sessionCode": session_data["sessionCode"], "participantUserId": user.idp_id},
            )
            if start_success and start_data["result"] and start_data["result"]["participantSessionUrl"]:
                return self.send_response({"session_redirect_url": start_data["result"]["participantSessionUrl"]})
            else:
                return self.send_error_response(start_data)


class ScheduledSessionManagementApiView(AppAPIView):
    """Api view to get list of scheduled sessions in a specific date and time."""

    serializer_class = SessionManagementSerializer

    def post(self, request, *args, **kwargs):
        """Returns the list of scheduled session."""

        user = self.get_user()
        validated_data = self.get_valid_serializer().validated_data
        live_sessions = []
        course = validated_data.get("course")
        # filter the queryset based on the user's current role & course provided
        qs_filter = Q(creator_role=RoleTypeChoices.admin)
        user_role_type = user.current_role.role_type
        if user_role_type == RoleTypeChoices.learner:
            qs_filter |= Q(creator_role=RoleTypeChoices.learner, user=user)
        if course:
            qs_filter &= Q(module__course=course)
        scheduled_sessions = ScheduledSession.objects.filter(qs_filter)

        session_payload = self.get_session_payload(validated_data)
        success, data = post_request(
            service="VIRTUTOR",
            url_path=settings.VIRTUTOR_CONFIG["get_all_session_url"],
            data=session_payload,
        )
        if not success:
            return self.send_error_response({"error": "Failed to fetch scheduled sessions."})
        result = data.get("result")
        sessions = result.get("sessions") if result else None
        if not sessions:
            error_message = "No scheduled sessions found in the given date."
            return self.send_error_response({"error": error_message})
        # iterate over all sessions to provide the session and trainer details
        for session in sessions:
            trainer_instance = Trainer.objects.filter(
                trainer_id=session["participants"][0]["participantUser"]["platformUserId"]
            ).first()
            scheduled_instance = scheduled_sessions.filter(scheduled_id=session["sessionScheduleId"]).first()
            if scheduled_instance:
                end_time = convert_utc_to_ist(session["endDate"])
                current_time = datetime.now()
                session.update({"startDate": convert_utc_to_ist(session["startDate"]), "endDate": end_time})
                if scheduled_instance.recording_days:
                    is_recording_available = (
                        scheduled_instance.end_date <= timezone.now()
                        and scheduled_instance.end_date + timedelta(days=scheduled_instance.recording_days)
                        >= timezone.now()
                    )
                else:
                    is_recording_available = scheduled_instance.end_date <= timezone.now()
                live_sessions.append(
                    {
                        "id": scheduled_instance.id,
                        "course": scheduled_instance.module.course.id,
                        "trainer_name": trainer_instance.first_name if trainer_instance else None,
                        "trainer_skills": trainer_instance.skills.get("skills") if trainer_instance else None,
                        "is_ended": True if current_time > end_time else False,
                        "is_recording_available": is_recording_available,
                        **session,
                    }
                )
        return self.send_response(live_sessions)

    def get_session_payload(self, validated_data):
        """Returns the session payload to get all the sessions"""
        return {
            "PageSize": 1000,
            "PageNumber": 1,
            "TenantId": get_current_tenant_idp_id(),
            "TimeZone": "India Standard Time",
            "SessionStatus": [1, 2, 3, 4, 7],
            "SessionTypes": [1, 2],
            "StartDate": format_datetime(validated_data["start_date"]),
            "EndDate": format_datetime(validated_data["end_date"]),
            "PlatformUserId": 0,
            "SessionType": 2,
            "ReadAll": False,
            "SearchTitle": None,
            "ViewType": 0,
        }


class SessionPaticipantListApiView(AppAPIView):
    """Api view to get list of scheduled session participants."""

    serializer_class = SimpleUserReadOnlyModelSerializer

    def get(self, request, *args, **kwargs):
        """Returns the list of scheduled session participants."""

        session_instance = get_object_or_404(ScheduledSession, id=kwargs.get("session_id", None))
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        success, data = get_virtutor_session_participant_list(
            scheduled_id=session_instance.scheduled_id,
            session_code=session_instance.session_code,
            auth_token=idp_token,
        )
        if not success:
            return self.send_error_response(data)
        user_idp_ids = [result["platformUserId"] for result in data["result"] if result.get("platformUserId")]
        response_data = self.serializer_class(User.objects.filter(idp_id__in=user_idp_ids), many=True).data
        return self.send_response(response_data)


class SessionPaticipantUpdateApiView(AppAPIView):
    """Api view to update the session participants."""

    class _Serializer(AppSerializer):
        """Serializer class for the same view."""

        participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.alive(), many=True)

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Handle on post."""

        session_instance = get_object_or_404(ScheduledSession, id=kwargs.get("session_id", None))
        validated_data = self.get_valid_serializer().validated_data
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        success, role_data = get_virtutor_roles_by_tenant(auth_token=idp_token)
        if not success:
            return self.send_error_response(role_data)
        mentee_role_id = next(role["roleId"] for role in role_data["result"] if role["roleName"] == "Mentee")
        payload = []
        for participant in validated_data["participants"]:
            payload.append(
                {
                    "isRemoved": False,
                    "participantMentorCode": None,
                    "participantSessionRole": 2,  # Mentee(Trainee)
                    "participantMoDRole": mentee_role_id,
                    "ParticipantTenantId": get_current_tenant_idp_id(),
                    "participantEmail": participant.email,
                    "participantName": participant.first_name,
                    "participantSurname": participant.last_name,
                    "participantUserId": participant.idp_id,
                }
            )
        success, data = post_request(
            service="VIRTUTOR",
            url_path=settings.VIRTUTOR_CONFIG["update_session_participant_url"],
            params={"tenantId": get_current_tenant_idp_id(), "sessionId": session_instance.scheduled_id},
            data=payload,
            auth_token=idp_token,
        )
        return self.send_response(data) if success else self.send_error_response(data)


class SessionRecordingsURLApiView(AppAPIView):
    """Api view to provide ended session recordings urls."""

    def get(self, request, *args, **kwargs):
        """Returns the virtutor session recordings urls."""

        session = get_object_or_404(ScheduledSession, id=kwargs.get("pk"))
        current_date = timezone.now()
        if current_date < session.end_date:
            return self.send_error_response("Session is not expired")
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        success, recordings_data = get_session_recordings_url(
            auth_token=idp_token, scheduled_id=session.scheduled_id, session_code=session.session_code
        )
        if not success:
            return self.send_error_response(recordings_data)
        return self.send_response(recordings_data)
