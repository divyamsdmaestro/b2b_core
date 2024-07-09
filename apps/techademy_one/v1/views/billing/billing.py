from apps.common.views.api import AppAPIView, NonAuthenticatedAPIMixin
from apps.learning.models.catalogue.catalogue import Catalogue
from apps.learning.models.expert.expert import Expert
from apps.my_learning.config import EnrollmentTypeChoices
from apps.my_learning.models import Enrollment
from apps.techademy_one.v1.serializers import T1BillingSerializer
from apps.tenant.models import Tenant
from apps.virtutor.models import Trainer


class T1BillingAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """
    Techademy One Api view to send stats for billing.
    eg:
        1. No of users enrolled in any type learnings.
        2. No of catalogues enrolled.
        3. No of courses enrolled.
        4. No of Learning Path enrolled.
        5. No of courses with Labs enrolled.
        6. No of courses with Mentor enrolled.
        7. No of courses with Expert enrolled.
    """

    serializer_class = T1BillingSerializer

    def post(self, request, *args, **kwargs):
        """Logic for the same."""

        data = self.get_valid_serializer().validated_data
        tenant_id, start_date, end_date = data["tenant_id"], data["start_date"], data["end_date"]
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Tenant not found."})
        tenant.activate_db()
        user_enrollments = self.get_total_unique_user_enrollments(start_date, end_date)
        catalogue_created = self.get_total_catalogues_created(start_date, end_date)
        course_enrollments = self.get_total_unique_course_enrollments(start_date, end_date)
        lp_enrollments = self.get_total_unique_lp_enrollments(start_date, end_date)
        course_with_labs_enrollments = self.get_total_unique_course_with_labs_enrollments(start_date, end_date)
        course_with_mentor_enrollments = self.get_total_unique_course_with_mentor_enrollments(start_date, end_date)
        course_with_expert_enrollments = self.get_total_unique_course_with_expert_enrollments(start_date, end_date)
        return self.send_response(
            data={
                "catalogue_created": catalogue_created,
                "user_enrollments": user_enrollments,
                "course_enrollments": course_enrollments,
                "learning_path_enrollments": lp_enrollments,
                "course_with_labs_enrollments": course_with_labs_enrollments,
                "course_with_mentor_enrollments": course_with_mentor_enrollments,
                "course_with_expert_enrollments": course_with_expert_enrollments,
            }
        )

    @staticmethod
    def get_total_unique_user_enrollments(start_date, end_date):
        """Returns the unique users who enrolled to the courses, LPs & ALPs in the specific duration."""

        return (
            Enrollment.objects.filter(
                created_at__date__range=(start_date, end_date),
                learning_type__in=[
                    EnrollmentTypeChoices.course,
                    EnrollmentTypeChoices.learning_path,
                    EnrollmentTypeChoices.advanced_learning_path,
                ],
            )
            .values_list("user_id", flat=True)
            .distinct()
            .count()
        )

    @staticmethod
    def get_total_unique_course_enrollments(start_date, end_date):
        """Returns the unique courses enrolled in the specific duration."""

        return (
            Enrollment.objects.filter(
                created_at__date__range=(start_date, end_date), learning_type=EnrollmentTypeChoices.course
            )
            .values_list("course_id", flat=True)
            .distinct()
            .count()
        )

    @staticmethod
    def get_total_unique_lp_enrollments(start_date, end_date):
        """Returns the unique LP enrolled in the specific duration."""

        return (
            Enrollment.objects.filter(
                created_at__date__range=(start_date, end_date), learning_type=EnrollmentTypeChoices.learning_path
            )
            .values_list("learning_path_id", flat=True)
            .distinct()
            .count()
        )

    @staticmethod
    def get_total_catalogues_created(start_date, end_date):
        """Returns the count of catalogues created in that tenant."""

        return Catalogue.objects.filter(created_at__date__range=(start_date, end_date)).count()

    @staticmethod
    def get_total_unique_course_with_labs_enrollments(start_date, end_date):
        """Returns the unique courses enrolled in the specific duration."""

        return (
            Enrollment.objects.filter(
                created_at__date__range=(start_date, end_date),
                learning_type=EnrollmentTypeChoices.course,
                course__mml_sku_id__isnull=False,
            )
            .values_list("course_id", flat=True)
            .distinct()
            .count()
        )

    @staticmethod
    def get_total_unique_course_with_mentor_enrollments(start_date, end_date):
        """Returns the unique courses enrolled in the specific duration."""

        return (
            Enrollment.objects.filter(
                created_at__date__range=(start_date, end_date),
                learning_type=EnrollmentTypeChoices.course,
                course__id__in=Trainer.objects.values_list("course__id", flat=True),
            )
            .values_list("course_id", flat=True)
            .distinct()
            .count()
        )

    @staticmethod
    def get_total_unique_course_with_expert_enrollments(start_date, end_date):
        """Returns the unique courses enrolled in the specific duration."""

        return (
            Enrollment.objects.filter(
                created_at__date__range=(start_date, end_date),
                learning_type=EnrollmentTypeChoices.course,
                course__id__in=Expert.objects.values_list("course__id", flat=True),
            )
            .values_list("course_id", flat=True)
            .distinct()
            .count()
        )
