from datetime import datetime

from django.conf import settings

from apps.common.tasks import BaseAppTask

LEARNING_FILTER_PARAMS = {
    "course": "module__course__id__in",
    "learning_path": "module__course__related_learning_path_courses__learning_path__id__in",
    "advanced_learning_path": "module__course__related_learning_path_courses__learning_path__related_alp_learning_paths__advanced_learning_path__id__in",  # noqa
}


class SessionParticipantUpdateTask(BaseAppTask):
    """Task to to update the session participants in virtutor."""

    def run(self, learning_type: str, learning_instance_id, user_id, idp_token: str, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User
        from apps.common.communicator import post_request
        from apps.tenant_service.middlewares import get_current_tenant_idp_id
        from apps.virtutor.helpers import get_virtutor_roles_by_tenant
        from apps.virtutor.models import ScheduledSession

        self.switch_db(db_name)
        self.logger.info("Executing SessionParticipantUpdateTask")

        current_date = datetime.now().date()
        if isinstance(user_id, int):
            user_id = [user_id]
        if isinstance(learning_instance_id, int):
            learning_instance_id = [learning_instance_id]
        scheduled_ids = ScheduledSession.objects.filter(
            **{LEARNING_FILTER_PARAMS[learning_type]: learning_instance_id}, end_date__date__gte=current_date
        ).values_list("scheduled_id", flat=True)
        users = User.objects.filter(id__in=user_id)
        tenant_id = get_current_tenant_idp_id()
        success, role_data = get_virtutor_roles_by_tenant(auth_token=idp_token)
        if not success:
            self.logger.info("Error while getting virtutor roles by tenant.")
            return False
        mentee_role_id = next(role["roleId"] for role in role_data["result"] if role["roleName"] == "Mentee")
        payload = []
        for user in users:
            payload.append(
                {
                    "isRemoved": False,
                    "participantMentorCode": None,
                    "participantSessionRole": 2,  # Mentee(Trainee)
                    "participantMoDRole": mentee_role_id,
                    "ParticipantTenantId": tenant_id,
                    "participantEmail": user.email,
                    "participantName": user.first_name,
                    "participantSurname": user.last_name,
                    "participantUserId": user.idp_id,
                }
            )
        for scheduled_id in scheduled_ids:
            post_request(
                service="VIRTUTOR",
                url_path=settings.VIRTUTOR_CONFIG["update_session_participant_url"],
                params={"tenantId": tenant_id, "sessionId": scheduled_id},
                data=payload,
                auth_token=idp_token,
            )
        return True
