from rest_framework import serializers

from apps.common.serializers import AppCreateModelSerializer, AppReadOnlyModelSerializer, BaseIDNameSerializer
from apps.learning.helpers import LEARNING_INSTANCE_MODELS
from apps.meta.models import FeedbackTemplateChoice, FeedbackTemplateQuestion
from apps.meta.serializers.v1 import FeedbackChoiceListSerializer, FeedbackQuestionListSerializer
from apps.my_learning.config import AllBaseLearningTypeChoices
from apps.my_learning.models import FeedbackResponse


class FeedbackResponseCreateSerializer(AppCreateModelSerializer):
    """Serializer Class for Feedback Response Create"""

    learning_type = serializers.ChoiceField(AllBaseLearningTypeChoices.choices, required=True)
    learning_type_id = serializers.CharField(required=True)
    question = serializers.PrimaryKeyRelatedField(
        queryset=FeedbackTemplateQuestion.objects.all(), required=False, allow_null=True
    )
    choice = serializers.PrimaryKeyRelatedField(
        queryset=FeedbackTemplateChoice.objects.all(), required=False, allow_null=True
    )
    text = serializers.CharField(required=False, allow_null=True)

    class Meta(AppCreateModelSerializer.Meta):
        model = FeedbackResponse
        fields = [
            "learning_type",
            "learning_type_id",
            "question",
            "choice",
            "text",
            "is_ccms_obj",
            "template_ccms_id",
            "question_ccms_id",
            "choice_ccms_id",
        ]

    def validate(self, attrs):
        """Function to validate response type"""

        learning_type = attrs.get("learning_type")
        learning_type_id = attrs.get("learning_type_id")
        if attrs.get("is_ccms_obj"):
            feedback_detail = self.context["feedback_detail"]
            if question_ccms_id := attrs.get("question_ccms_id"):
                response_type = feedback_detail["question"][question_ccms_id]["response_type"]
            else:
                raise serializers.ValidationError({"question_ccms_id": "This field is required."})
            if response_type == "choice":
                response_type_field = "choice_ccms_id"
            else:
                response_type_field = "text"
        else:
            if not attrs.get("question"):
                raise serializers.ValidationError({"question": "This field is required."})
            question = attrs.get("question")
            choice = attrs.get("choice")
            if choice and choice.question != question:
                raise serializers.ValidationError({"choice": "Choice is not related to the question."})
            response_type_field = question.response_type
        if not attrs.get("is_ccms_obj") and not LEARNING_INSTANCE_MODELS[learning_type].objects.filter(
            id=learning_type_id
        ):
            raise serializers.ValidationError({"learning_type": f"Invalid {learning_type}"})
        if not attrs.get(response_type_field):
            raise serializers.ValidationError({f"{response_type_field}": "This field is required"})
        attrs["user"] = self.get_user()
        return attrs


class FeedbackResponseListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to detail User's Feedback Response"""

    question = FeedbackQuestionListSerializer(read_only=True)
    choice = FeedbackChoiceListSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = FeedbackResponse
        fields = ["id", "question", "choice", "text"]


class FeedbackResponseTemplateListSerializer(AppReadOnlyModelSerializer):
    """Serializer class to List Feedback Response"""

    user = BaseIDNameSerializer()
    template = serializers.SerializerMethodField(read_only=True)
    learning_obj = serializers.SerializerMethodField(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = FeedbackResponse
        fields = [
            "id",
            "user",
            "learning_type",
            "learning_type_id",
            "template",
            "learning_obj",
            "is_ccms_obj",
            "template_ccms_id",
        ]

    def get_template(self, obj):
        """Funtion to get template"""

        return (
            {"id": None, "name": "CCMS Feedback"}
            if obj.is_ccms_obj
            else BaseIDNameSerializer(obj.question.feedback_template).data
        )

    def get_learning_obj(self, obj):
        """funtion to get learning type object"""

        if obj.is_ccms_obj:
            return {"id": None, "name": "CCMS Learning"}
        else:
            learning_obj = LEARNING_INSTANCE_MODELS[obj.learning_type].objects.filter(id=obj.learning_type_id).first()
            return BaseIDNameSerializer(learning_obj).data
