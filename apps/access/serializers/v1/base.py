from rest_framework import serializers

from apps.access.models import User, UserDetail, UserProfilePicture
from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSpecificImageFieldSerializer,
    AppUpdateModelSerializer,
    BaseIDNameSerializer,
)


class CommonUserUpdateSerializer(AppUpdateModelSerializer):
    """Common `User` model update serializer."""

    last_name = serializers.CharField(required=False)

    class Meta(AppUpdateModelSerializer.Meta):
        model = User
        fields = ["first_name", "middle_name", "last_name", "email", "profile_picture", "user_details"]


class CommonUserDetailUpdateSerializer(AppUpdateModelSerializer):
    """Common `UserDetail` model update serializer."""

    promotion_date = serializers.DateField(required=False, allow_null=True)
    certifications = serializers.CharField(required=False, allow_null=True)

    class Meta(AppUpdateModelSerializer.Meta):
        model = UserDetail
        fields = [
            "contact_number",
            "gender",
            "birth_date",
            "current_address",
            "current_country",
            "current_state",
            "current_city",
            "current_pincode",
            "promotion_date",
            "certifications",
        ]


# TODO: Need to retrive image from get_image function
class UserProfilePictureRetrieveSerializer(AppReadOnlyModelSerializer):
    """Serializer class to retrieve User Profile image."""

    class Meta:
        model = UserProfilePicture
        fields = [
            "id",
            "image",
        ]


class SimpleUserReadOnlyModelSerializer(AppReadOnlyModelSerializer):
    """Lightweight Serializer class for the `User` model."""

    roles = BaseIDNameSerializer(read_only=True, many=True)
    profile_picture = UserProfilePictureRetrieveSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = [
            "id",
            "uuid",
            "idp_id",
            "name",
            "roles",
            "email",
            "profile_picture",
        ]


class CommonLearningDashboardSerializer(AppReadOnlyModelSerializer):
    """Serializer class for Common Learnings."""

    image = AppSpecificImageFieldSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = ["id", "name", "proficiency", "image", "category"]
