from django.db.models import Q
from rest_framework import serializers

from apps.common.helpers import unpack_dj_choices
from apps.my_learning.config import LearningStatusChoices, RatingTypeChoices
from apps.my_learning.models import UserRating
from apps.my_learning.serializers.v1.tracker.common import BaseLearningFKCUDModelSerializer


class UserRatingCUDSerializer(BaseLearningFKCUDModelSerializer):
    """Serializer class for CUD user Ratings."""

    class Meta(BaseLearningFKCUDModelSerializer.Meta):
        model = UserRating
        fields = BaseLearningFKCUDModelSerializer.Meta.fields + [
            "learning_type",
            "rating",
        ]

    def validate(self, attrs):
        """Validate if the selected learning_type corresponding field is not empty."""

        learning_type = attrs["learning_type"]
        if not attrs.get(learning_type, None):
            raise serializers.ValidationError({f"{learning_type}": "This field is required."})
        if not attrs[learning_type].is_rating_enabled:
            raise serializers.ValidationError({f"{learning_type}": f"Rating is not enabled for this {learning_type}."})
        user = self.get_user()
        user_groups = user.related_user_groups.all().values_list("id", flat=True)
        if not attrs[learning_type].related_enrollments.filter(
            Q(user_group__in=user_groups) | Q(user=user), learning_status=LearningStatusChoices.completed
        ):
            raise serializers.ValidationError(
                {f"{learning_type}": f"You need to complete the {learning_type} before giving a rating."}
            )
        return attrs

    def create(self, validated_data):
        """If rating already present then just update."""

        user = self.get_user()
        validated_data["user"] = user
        learning_type = validated_data["learning_type"]
        instance = validated_data[learning_type].related_user_ratings.filter(user=user).first()
        if not instance:
            instance = super().create(validated_data)
        else:
            instance.rating = validated_data["rating"]
            instance.save()
        return instance

    def get_meta(self) -> dict:
        """get meta data."""

        return {
            "learning_type": unpack_dj_choices(RatingTypeChoices.choices),
        }
