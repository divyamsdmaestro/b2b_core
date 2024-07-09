from django.db.models import Q
from django.utils import timezone

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import ApprovalTypeChoices, EnrollmentTypeChoices, LearningStatusChoices
from apps.my_learning.tasks import UserEnrollmentEmailTask


class UserBulkEnrollTask(BaseAppTask):
    """Task to enroll the users to course, lp, alp...."""

    db_name = None
    token = None
    request_headers = None

    def register_users_in_chat_learnings(self, is_user, user_or_group, learning_instance):
        """Register users in chat service."""

        from apps.common.helpers import process_request_headers
        from apps.tenant_service.middlewares import get_current_tenant_details

        tenant_details = get_current_tenant_details()
        if tenant_details["is_keycloak"]:
            if is_user:
                user_id = [user_or_group.uuid]
            else:
                user_id = list(user_or_group.members.all().values_list("uuid", flat=True))
        else:
            if is_user:
                user_id = [user_or_group.idp_id]
            else:
                user_id = list(user_or_group.members.all().values_list("idp_id", flat=True))
        chat_request_headers = process_request_headers(self.request_headers)
        learning_instance.register_user_to_course_in_chat(user_id=user_id, request_headers=chat_request_headers)
        return True

    def create_enrollments(self, user_or_group, items, learning_type, default_enrollment_args):
        """Performs enrollment creation for given inputs."""

        from apps.access.models import User
        from apps.event.config import CalendarEventTypeChoices
        from apps.my_learning.models import Enrollment
        from apps.my_learning.serializers.v1 import tracker_related_fields
        from apps.my_learning.tasks import CalendarActivityCreationTask

        is_user = isinstance(user_or_group, User)
        for item in items:
            default_enrollment_args["learning_type"] = learning_type
            try:
                if is_user:
                    user_groups = user_or_group.related_user_groups.all()
                    if Enrollment.objects.filter(
                        Q(user_group__in=user_groups) | Q(user=user_or_group), **{learning_type: item}
                    ):
                        continue
                enrollment, created = user_or_group.related_enrollments.get_or_create(
                    **{learning_type: item}, defaults=default_enrollment_args
                )
                learning_instance = getattr(enrollment, enrollment.learning_type)
                if created:
                    enrollment.notify_user()
                    if enrollment.learning_type in [EnrollmentTypeChoices.course]:
                        self.register_users_in_chat_learnings(
                            is_user=is_user,
                            user_or_group=user_or_group,
                            learning_instance=learning_instance,
                        )
                if enrollment.learning_type in [
                    CalendarEventTypeChoices.course,
                    CalendarEventTypeChoices.learning_path,
                    CalendarEventTypeChoices.advanced_learning_path,
                ]:
                    CalendarActivityCreationTask().run_task(
                        event_type=enrollment.learning_type,
                        event_instance_id=learning_instance.id,
                        user_ids=user_or_group.id
                        if is_user
                        else list(user_or_group.members.all().values_list("id", flat=True)),
                        db_name=self.db_name,
                    )
                if is_user:
                    tracker_instance = (
                        getattr(user_or_group, tracker_related_fields[enrollment.learning_type])
                        .filter(**{enrollment.learning_type: learning_instance.id if learning_instance else None})
                        .first()
                    )
                    if tracker_instance:
                        enrollment.learning_status = LearningStatusChoices.started
                        enrollment.save()
                self.logger.info(f"**{learning_type} {item.name} enrolled successfully for {user_or_group}.")
            except Exception:  # noqa
                enrollment = None
                self.logger.info(f"**{learning_type} {item.name} enrollment failed for {user_or_group}.")
            if enrollment and is_user:
                UserEnrollmentEmailTask().run_task(
                    user_id=user_or_group.id, enrollment_id=enrollment.id, db_name=self.db_name
                )
                enrollment.call_leaderboard_tasks(is_assigned=True, request_headers=self.request_headers)
            elif enrollment and not is_user:
                UserEnrollmentEmailTask().run_task(
                    user_group_id=user_or_group.id, enrollment_id=enrollment.id, db_name=self.db_name
                )
        return True

    def process_enrollments(self, groups_or_users, items, default_enrollment_args):
        """Process the given data for enrollment."""

        from apps.access.models import User
        from apps.tenant_service.middlewares import get_current_db_name
        from apps.virtutor.tasks import SessionParticipantUpdateTask

        user_ids = []
        learning_type_and_ids = {
            EnrollmentTypeChoices.course: [],
            EnrollmentTypeChoices.learning_path: [],
            EnrollmentTypeChoices.advanced_learning_path: [],
        }
        for group_or_user in groups_or_users:
            if isinstance(group_or_user, User):
                user_ids.append(group_or_user.id)
            else:
                user_ids += list(group_or_user.members.values_list("id", flat=True))
            for course in items["course"]:
                learning_type = EnrollmentTypeChoices.course
                self.create_enrollments(group_or_user, [course], learning_type, default_enrollment_args)
                learning_type_and_ids[learning_type].append(course.id)
            for learning_path in items["learning_path"]:
                learning_type = EnrollmentTypeChoices.learning_path
                self.create_enrollments(group_or_user, [learning_path], learning_type, default_enrollment_args)
                learning_type_and_ids[learning_type].append(learning_path.id)
            for alp in items["alp"]:
                learning_type = EnrollmentTypeChoices.advanced_learning_path
                self.create_enrollments(group_or_user, [alp], learning_type, default_enrollment_args)
                learning_type_and_ids[learning_type].append(alp.id)
            for st in items["skill_traveller"]:
                self.create_enrollments(
                    group_or_user, [st], EnrollmentTypeChoices.skill_traveller, default_enrollment_args
                )
            for playground in items["playground"]:
                self.create_enrollments(
                    group_or_user, [playground], EnrollmentTypeChoices.playground, default_enrollment_args
                )
            for pg in items["playground_group"]:
                self.create_enrollments(
                    group_or_user, [pg], EnrollmentTypeChoices.playground_group, default_enrollment_args
                )
            for assignment in items["assignment"]:
                self.create_enrollments(
                    group_or_user, [assignment], EnrollmentTypeChoices.assignment, default_enrollment_args
                )
            for assignment_group in items["assignment_group"]:
                self.create_enrollments(
                    group_or_user, [assignment_group], EnrollmentTypeChoices.assignment_group, default_enrollment_args
                )
        for learning_type, learning_ids in learning_type_and_ids.items():
            if learning_ids:
                SessionParticipantUpdateTask().run_task(
                    learning_type=learning_type,
                    learning_instance_id=learning_ids,
                    user_id=user_ids,
                    idp_token=self.token,
                    db_name=get_current_db_name(),
                )
        return True

    def run(self, data, authenticated_user, db_name, **kwargs):
        """Run handler."""

        from apps.access.models import User
        from apps.my_learning.serializers.v1 import UserBulkEnrollSerializer

        self.switch_db(db_name)
        self.db_name = db_name
        self.token = kwargs.get("token")
        self.request_headers = kwargs.get("request", None)
        serializer = UserBulkEnrollSerializer(data=data)
        serializer.is_valid()
        validated_data = serializer.validated_data
        authenticated_user = User.objects.filter(pk=authenticated_user).first()
        default_enrollment_args = {
            "created_by": authenticated_user,
            "action": "approved",
            "action_date": timezone.now().date(),
            "reason": "Bulk enrollment process",
            "actionee_id": authenticated_user.id if authenticated_user else None,
            "approval_type": ApprovalTypeChoices.tenant_admin,
            "is_enrolled": True,
            "end_date": validated_data["end_date"],
        }
        self.process_enrollments(validated_data["user_group"], validated_data, default_enrollment_args)
        self.process_enrollments(validated_data["users"], validated_data, default_enrollment_args)
        return True
