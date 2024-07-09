from rest_framework import serializers

from apps.common.helpers import unpack_dj_choices
from apps.learning.models import Category, CategoryRole, CategorySkill
from apps.my_learning.config import FavouriteTypeChoices
from apps.my_learning.models import UserFavourite
from apps.my_learning.serializers.v1 import BaseLearningFKCUDModelSerializer


class UserFavouriteSerializer(BaseLearningFKCUDModelSerializer):
    """Serializer class for add to favourites."""

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.alive(),
        required=False,
    )
    skill = serializers.PrimaryKeyRelatedField(
        queryset=CategorySkill.objects.alive(),
        required=False,
    )
    role = serializers.PrimaryKeyRelatedField(
        queryset=CategoryRole.objects.alive(),
        required=False,
    )

    class Meta(BaseLearningFKCUDModelSerializer.Meta):
        model = UserFavourite
        fields = BaseLearningFKCUDModelSerializer.Meta.fields + [
            "favourite_type",
            "category",
            "skill",
            "role",
        ]

    def validate(self, attrs):
        """Validate if the selected favourite_type corresponding field is not empty."""

        favourite_type = attrs.get("favourite_type")
        if not attrs.get(favourite_type, None):
            raise serializers.ValidationError({f"{favourite_type}": "This field is required."})
        user = self.get_user()
        if attrs[favourite_type].related_user_favourites.filter(user=user, favourite_type=favourite_type):
            raise serializers.ValidationError({f"{favourite_type}": "Already added to favourites."})
        attrs["user"] = user
        return attrs

    def get_meta(self) -> dict:
        """get meta data."""

        return {
            "favourite_type": unpack_dj_choices(FavouriteTypeChoices.choices),
        }
