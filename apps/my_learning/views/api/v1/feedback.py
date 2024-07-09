from apps.common.views.api import AppModelCreateAPIViewSet, AppModelListAPIViewSet
from apps.learning.helpers import get_ccms_retrieve_details
from apps.my_learning.helpers import get_ccms_list_details
from apps.my_learning.models import FeedbackResponse
from apps.my_learning.serializers.v1 import (
    FeedbackResponseCreateSerializer,
    FeedbackResponseListSerializer,
    FeedbackResponseTemplateListSerializer,
)


class FeedbackResponseCreateApiViewset(AppModelCreateAPIViewSet):
    """Create View for User's Feedback Response"""

    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseCreateSerializer

    def create(self, request, *args, **kwargs):
        """Overridden to create Feedback responses"""

        context = self.get_serializer_context()
        if request.data[0].get("is_ccms_obj"):
            success, data = get_ccms_retrieve_details(
                learning_type="feedback",
                instance_id=request.data[0].get("template_ccms_id"),
                request={"headers": dict(request.headers)},
            )
            if success:
                context["feedback_detail"] = data["data"]
            else:
                return self.send_error_response(data=data)
        serializer = self.get_serializer(data=request.data, many=True, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.send_response("success")


class UserFeedbackTemplateListApiViewset(AppModelListAPIViewSet):
    """List Viewset to get Feedback Responses"""

    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseTemplateListSerializer
    filterset_fields = ["learning_type", "learning_type_id", "user", "is_ccms_obj"]
    search_fields = ["user__first_name", "user__last_name"]

    def get_queryset(self):
        """overridden to get unique responses"""

        queryset = (
            super()
            .get_queryset()
            .order_by("learning_type", "learning_type_id", "user_id")
            .distinct("learning_type", "learning_type_id", "user_id")
        )
        return queryset

    def list(self, request, *args, **kwargs):
        """Include CCMS Feedback details."""

        response = super().list(request, *args, **kwargs)
        feedbacks = response.data["data"]["results"]
        ccms_obj_available = False
        index = 0
        feedback_ids, template_uuids = [], []
        query_params = {"course": [], "learning_path": [], "advanced_learning_path": []}
        for feedback in feedbacks:
            if feedback["is_ccms_obj"]:
                ccms_obj_available = True
                query_params[feedback["learning_type"]].append(feedback["learning_type_id"])
                template_uuids.append(feedback["template_ccms_id"])
                feedback_ids.append(index)
            index += 1
        if ccms_obj_available:
            success, learnings_list = get_ccms_list_details(
                learning_type="common_learning",
                request={"headers": request.headers},
                params=query_params,
            )
            if not success:
                return self.send_error_response(learnings_list)
            success, template_list = get_ccms_list_details(
                learning_type="feedback",
                request={"headers": request.headers},
                params={"uuid": template_uuids},
            )
            if not success:
                return self.send_error_response(template_list)
            for feedback_id in feedback_ids:
                feedback_data = feedbacks[feedback_id]
                template_data = (
                    learnings_list["data"].get(feedback_data["learning_type"]).get(feedback_data["learning_type_id"])
                )
                if template_data:
                    feedback_data["learning_obj"] = template_data
                    feedback_data["template"] = template_list["data"][feedback_data["template_ccms_id"]]
        return response


class UserFeedbackResponseListApiViewset(AppModelListAPIViewSet):
    """Detail Viewset to get Feedback Responses"""

    queryset = FeedbackResponse.objects.all().order_by("created_at")
    serializer_class = FeedbackResponseListSerializer
    filterset_fields = ["user", "question__feedback_template", "learning_type", "learning_type_id", "is_ccms_obj"]

    def list(self, request, *args, **kwargs):
        """Overriden to give support for ccms feedback response."""

        if request.query_params.get("is_ccms_obj") == "true":
            template_id = request.query_params.get("template_ccms_id")
            user = request.query_params.get("user")
            learning_type = request.query_params.get("learning_type")
            learning_type_id = request.query_params.get("learning_type_id")
            response_data = []
            feedback_reponses = FeedbackResponse.objects.filter(
                user=user, learning_type=learning_type, learning_type_id=learning_type_id, is_ccms_obj=True
            ).order_by("created_at")
            success, data = get_ccms_retrieve_details(
                learning_type="feedback",
                instance_id=template_id,
                request={"headers": dict(request.headers)},
            )
            if not success:
                return self.send_error_response(data=data)
            feedback_questions = data["data"]["question"]
            for feedback_reponse in feedback_reponses:
                if feedback_questions.get(feedback_reponse.question_ccms_id):
                    question_data = feedback_questions[feedback_reponse.question_ccms_id]
                    choice_data = None
                    for choice in question_data["choice"]:
                        if choice["uuid"] == feedback_reponse.choice_ccms_id:
                            choice_data = choice
                            break
                    response_data.append(
                        {
                            "id": feedback_reponse.id,
                            "uuid": feedback_reponse.uuid,
                            "question": question_data,
                            "text": feedback_reponse.text,
                            "choice": choice_data,
                        }
                    )
            return self.send_response({"results": response_data})
        else:
            response = super().list(request, *args, **kwargs)
            return response
