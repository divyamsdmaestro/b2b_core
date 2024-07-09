from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.meta.config import FeedBackTypeChoices
from apps.meta.models import FeedbackTemplate, FeedbackTemplateChoice, FeedbackTemplateQuestion


class FeedbackChoiceListSerializer(AppReadOnlyModelSerializer):
    """List serializer to retrieve choices for Feedback Questions"""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = FeedbackTemplateChoice
        fields = ["id", "uuid", "choice"]


class FeedbackQuestionListSerializer(AppReadOnlyModelSerializer):
    """List serializer to retrieve Questions for Feedback Template"""

    choice = serializers.SerializerMethodField(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = FeedbackTemplateQuestion
        fields = ["id", "uuid", "question", "response_type", "choice"]

    def get_choice(self, obj):
        """Function to get choices for questions"""

        choice = obj.related_question_choices.order_by("created_at")
        return FeedbackChoiceListSerializer(choice, many=True).data


class FeedbackRetrieveSerializer(AppReadOnlyModelSerializer):
    """List Serializer for Feedback Model"""

    question = serializers.SerializerMethodField(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = FeedbackTemplate
        fields = ["id", "uuid", "name", "description", "question"]

    def get_question(self, obj):
        """Function to get Questions for template"""

        question = obj.related_template_questions.order_by("created_at")
        return FeedbackQuestionListSerializer(question, many=True).data


class FeedbackChoiceCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to retrieve Choices for Questions"""

    instance_id = serializers.IntegerField(allow_null=True, required=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = FeedbackTemplateChoice
        fields = ["instance_id", "choice"]


class FeedbackQuestionCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class to retrieve Question for Feedback"""

    choice = FeedbackChoiceCUDSerializer(many=True, required=False)
    instance_id = serializers.IntegerField(allow_null=True, required=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = FeedbackTemplateQuestion
        fields = ["instance_id", "question", "response_type", "choice"]

    def validate(self, attrs):
        """Validation to raise Choice as a required field
        if response type is choice"""

        if attrs["response_type"] == FeedBackTypeChoices.choice:
            if not attrs.get("choice"):
                raise serializers.ValidationError({"choice": "This Field is required"})
        return attrs


class FeedbackCUDSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for Feedback model CUD."""

    question = FeedbackQuestionCUDSerializer(many=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = FeedbackTemplate
        fields = ["name", "description", "question"]

    def create(self, validated_data):
        """Overridden to create Feedback Template"""

        questions_data = validated_data.pop("question", [])
        instance = super().create(validated_data=validated_data)
        for question in questions_data:
            question.pop("instance_id")
            choices_data = question.pop("choice", [])
            question = instance.related_template_questions.create(**question)
            for choices in choices_data:
                choices.pop("instance_id")
                question.related_question_choices.create(**choices)
        return instance

    def update(self, instance, validated_data):
        """Overridden to update Feedback Template"""

        questions_data = validated_data.pop("question", [])
        instance = super().update(instance=instance, validated_data=validated_data)
        updated_question_ids = []
        for questions in questions_data:
            question_id = questions.pop("instance_id")
            updated_question_ids.append(question_id)
            choices_data = questions.pop("choice", [])
            question, created = instance.related_template_questions.update_or_create(
                pk=question_id, defaults=questions
            )
            if created:
                updated_question_ids.append(question.id)
            if questions["response_type"] == FeedBackTypeChoices.choice:
                updated_choice_ids = []
                for choices in choices_data:
                    choice_id = choices.pop("instance_id")
                    updated_choice_ids.append(choice_id)
                    choice, created = question.related_question_choices.update_or_create(
                        pk=choice_id, defaults=choices
                    )
                    if created:
                        updated_choice_ids.append(choice.id)
                question.related_question_choices.exclude(id__in=updated_choice_ids).delete()
            else:
                question.related_question_choices.all().delete()
        instance.related_template_questions.exclude(id__in=updated_question_ids).delete()

        return instance

    def get_meta_initial(self):
        """Overridden to add the details of Feedback Template initial data."""

        return FeedbackRetrieveSerializer(self.instance).data

    def get_meta(self) -> dict:
        """Returns the meta data."""

        return {
            "response_type": self.serialize_dj_choices(FeedBackTypeChoices.choices),
        }
