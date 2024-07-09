from django.db.models import Avg, Q

from apps.access.serializers.v1.base import SimpleUserReadOnlyModelSerializer
from apps.common.views.api.base import AppAPIView
from apps.my_learning.models import CAYakshaResult, Enrollment, LPAYakshaResult
from apps.my_learning.serializers.v1 import (
    OneProfileCourseAssessmentSerializer,
    OneProfileCourseInfoSerializer,
    OneProfileLPAssessmentSerializer,
    OneProfileUserInfoSerializer,
)


class OneProfileUserInfoAPIView(AppAPIView):
    """Api view to get user's one profile data."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()

        return self.send_response(
            {
                "user": SimpleUserReadOnlyModelSerializer(user).data,
                "user_detail": OneProfileUserInfoSerializer(user.related_user_details).data
                if user.related_user_details
                else None,
            }
        )


class OneProfileAssessmentInfoAPIView(AppAPIView):
    """Api view to get user's one profile assessment data."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        ca_results = CAYakshaResult.objects.filter(
            Q(schedule__tracker__course_tracker__user=user)
            | Q(schedule__tracker__module_tracker__course_tracker__user=user)
        )
        lpa_results = LPAYakshaResult.objects.filter(schedule__tracker__user=user)

        return self.send_response(
            {
                "total_completed_assessment": ca_results.count() + lpa_results.count(),
                "total_passed_assessment": ca_results.filter(is_pass=True).count()
                + lpa_results.filter(is_pass=True).count(),
                "average_assessment_score": ca_results.aggregate(avg_progress=Avg("progress"))["avg_progress"],
                "ca_results_data": OneProfileCourseAssessmentSerializer(ca_results, many=True).data,
                "lpa_results_data": OneProfileLPAssessmentSerializer(lpa_results, many=True).data,
            }
        )


class OneProfileCourseInfoAPIView(AppAPIView):
    """Api view to get user's one profile course data."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        enrollment_ids = Enrollment.objects.filter(Q(user_group__in=user_groups) | Q(user=user)).values_list(
            "id", flat=True
        )
        completed_course_objs = user.related_user_course_trackers.filter(
            enrollment_id__in=enrollment_ids,
            is_completed=True,
        )[:5]
        return self.send_response(
            {"course_list": OneProfileCourseInfoSerializer(completed_course_objs, many=True).data}
        )
