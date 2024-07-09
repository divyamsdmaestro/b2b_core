from django.db.models import Q, Sum

from apps.access.models import User
from apps.common.views.api import AppAPIView, AppModelListAPIViewSet, NonAuthenticatedAPIMixin
from apps.leaderboard.models import BadgeActivity
from apps.leaderboard.serializers.v1 import BadgeActivityListSerializer
from apps.learning.models import Course
from apps.my_learning.models import UserCourseTracker
from apps.techademy_one.v1.serializers import T1UserCourseListSerializer
from apps.tenant.models import Tenant


class T1UserTotalLearningHourAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to send total time spent by the user on the platform."""

    def get(self, request, *args, **kwargs):
        """Logic for the same."""

        tenant_id, user_id = request.query_params.get("tenant_id"), request.query_params.get("user_id")
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Tenant not found."})
        tenant.activate_db()
        user = User.objects.filter(uuid=user_id).first()
        if not user:
            return self.send_error_response(data={"message": "User not found."})
        completed_courses = user.related_user_course_trackers.filter(is_completed=True)
        total_course_duration = (
            completed_courses.aggregate(total_course_duration=Sum("course__duration"))["total_course_duration"] or 0
        )
        return self.send_response({"learning_hours": total_course_duration / 3600})


class T1UserCourseListAPIViewSet(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """Api view to list user learning progress details."""

    serializer_class = T1UserCourseListSerializer
    queryset = Course.objects.active()

    def get_serializer_context(self):
        """Include the user course tracker list."""

        context = super().get_serializer_context()
        user_id = self.request.query_params.get("user_id")
        context["course_trackers"] = UserCourseTracker.objects.filter(user__uuid=user_id)
        return context

    def get_queryset(self):
        """Overridden to filter course trackers based on user_id and tenant_id."""

        queryset = super().get_queryset()
        tenant_id, user_id = self.request.query_params.get("tenant_id"), self.request.query_params.get("user_id")
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return queryset.none()
        tenant.activate_db()
        user = User.objects.filter(uuid=user_id).first()
        if not user:
            return queryset.none()
        self.request.user = user
        user_groups = user.related_user_groups.all()
        queryset = queryset.filter(
            Q(related_learning_catalogues__related_catalogue_relations__user_group__in=user_groups)
            | Q(related_learning_catalogues__related_catalogue_relations__user=user)
            | Q(related_enrollments__user=user)
            | Q(related_enrollments__user_group__in=user_groups)
        ).distinct()
        return queryset


class T1UserAssessmentResultAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to fetch user assessment result details."""

    def get(self, request, *args, **kwargs):
        """Logic for the same."""

        tenant_id, user_id = request.query_params.get("tenant_id"), request.query_params.get("user_id")
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Tenant not found."})
        tenant.activate_db()
        user = User.objects.filter(uuid=user_id).first()
        if not user:
            return self.send_error_response(data={"message": "User not found."})
        return self.send_response()


class T1OverallLearningAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Techademy One Api view to fetch courses , skill and learning path details."""

    def get(self, request, *args, **kwargs):
        """Logic for the same."""

        tenant_id, search = request.query_params.get("tenant_id"), request.query_params.get("search")
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return self.send_error_response(data={"message": "Tenant not found."})
        tenant.activate_db()
        response_data = {"course_details": search, "skills_details": [], "learning_path_details": []}
        return self.send_response(data=response_data)


class T1BadgeActivityListApiViewSet(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """Api Viewset to list Badge."""

    queryset = BadgeActivity.objects.all()
    serializer_class = BadgeActivityListSerializer

    def get_queryset(self):
        """Overridden to filter course trackers based on user_id and tenant_id."""

        queryset = super().get_queryset()
        tenant_id, user_id = self.request.query_params.get("tenant_id"), self.request.query_params.get("user_id")
        tenant = Tenant.objects.filter(uuid=tenant_id).first()
        if not tenant:
            return queryset.none()
        tenant.activate_db()
        user = User.objects.filter(uuid=user_id).first()
        if not user:
            return queryset.none()
        return user.related_badge_activities.all()
