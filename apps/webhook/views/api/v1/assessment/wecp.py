from datetime import datetime

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from apps.access.models import User
from apps.common.communicator import get_request
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.leaderboard.config import BadgeLearningTypeChoices
from apps.my_learning.helpers import assessment_tracker_progress_update
from apps.my_learning.models import CourseAssessmentTracker
from apps.tenant.models import TenantConfiguration


class CAWecpWebhookApiView(NonAuthenticatedAPIMixin, AppAPIView):
    """Webhook to get the result of the assessment from wecp."""

    def post(self, request, *args, **kwargs):
        """Get the results and storing the results to our system."""

        wecp_key = self.request.headers.get("Wepc-Webhook-Key", None)
        tenant_config = TenantConfiguration.objects.filter(wecp_key=wecp_key).first()
        if not tenant_config:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        tenant_config.tenant.activate_db()
        data = self.request.data
        assessment_id = data["quizId"]
        user_email = data["candidateDetails"]["Email"]
        start_time = data["testStartTime"]
        end_time = data["finishTime"]
        total_questions = 0
        assessment_score = data["score"]
        total_score = 0
        success, assessment_data = get_request(
            service="WECP",
            url_path=f"{settings.WECP_CONFIG['get_assessment_details']}{assessment_id}",
            auth_token=wecp_key,
        )
        if success:
            total_score = assessment_data["maxScore"] or 0
            total_questions = assessment_data["questionCount"]
        user = User.objects.filter(email=user_email).first()
        if user:
            assessment_tracker = CourseAssessmentTracker.objects.filter(
                assessment_uuid=assessment_id,
                course_tracker__user=user,
            ).first()
            if assessment_tracker:
                schedule = assessment_tracker.related_ca_yaksha_schedules.first()
                if schedule:
                    progress = round((int(assessment_score) / int(total_score)) * 100) if total_score != 0 else 0
                    is_pass = True if progress >= 60 else False
                    attempt = schedule.related_ca_yaksha_results.count() + 1
                    duration = 0
                    if start_time and end_time:
                        start_time = datetime.fromisoformat(start_time.rstrip("Z"))
                        end_time = datetime.fromisoformat(end_time.rstrip("Z"))
                        duration = (end_time - start_time).total_seconds()
                    schedule.related_ca_yaksha_results.update_or_create(
                        defaults={
                            "attempt": attempt,
                            "progress": 100 if progress > 100 else progress,
                            "duration": duration,
                            "total_questions": total_questions,
                            "answered": 0,
                            "start_time": start_time,
                            "end_time": end_time,
                            "is_pass": is_pass,
                        }
                    )
                    result_instance = schedule.related_ca_yaksha_results.all()
                    assessment_tracker_progress_update(
                        tracker=assessment_tracker,
                        result_instance=result_instance,
                        learning_type=BadgeLearningTypeChoices.course,
                        request=None,
                        user_id=user.id,
                    )
                    return self.send_response("success")

            return self.send_error_response("Tracker not found.")
        return self.send_error_response("User not found")
