from rest_framework import serializers

from apps.access.models import User
from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer, UserProfilePictureRetrieveSerializer
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.leaderboard.config import ASSESSMENT_BADGES_RANGE, MML_BADGES_RANGE, BadgeCategoryChoices, BadgeTypeChoices
from apps.leaderboard.models import Badge, BadgeActivity
from apps.learning.config import BadgeProficiencyChoices


class BadgeCommonModelSerializer(AppWriteOnlyModelSerializer):
    """`Badge` model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Badge
        fields = [
            "points",
        ]

    @staticmethod
    def validate_proficiency_against_points(category, badge_type, proficiency, points):
        """Validate logic for Video & Assessment based badges."""

        prev_prof_choice = BadgeProficiencyChoices.get_previous_choice(proficiency)
        if not prev_prof_choice:
            return None
        prev_proficiency = Badge.objects.filter(
            category=category, type=badge_type, proficiency=prev_prof_choice
        ).first()
        if not prev_proficiency:
            prev_prof_label = BadgeProficiencyChoices.get_choice(prev_prof_choice).label
            msg = f"{prev_prof_label} proficiency Badge is missing. Please add it first."
            raise serializers.ValidationError({"proficiency": msg})
        elif prev_proficiency.points >= points:
            raise serializers.ValidationError({"points": f"Points should be greater than {prev_proficiency.points}."})

    def get_meta(self) -> dict:
        """Get meta & initial values for `Leaderboard`."""

        return {
            "category": self.serialize_dj_choices(BadgeCategoryChoices.choices),
            "type": self.serialize_dj_choices(BadgeTypeChoices.choices),
            "proficiency": self.serialize_dj_choices(BadgeProficiencyChoices.choices),
            "mml": MML_BADGES_RANGE,
            "assessment": ASSESSMENT_BADGES_RANGE,
        }


class BadgeCreateModelSerializer(BadgeCommonModelSerializer):
    """`Badge` model serializer holds create, update & destroy."""

    class Meta(BadgeCommonModelSerializer.Meta):
        fields = BadgeCommonModelSerializer.Meta.fields + [
            "category",
            "type",
            "proficiency",
        ]

    @staticmethod
    def validate_badge_type(badge_type):
        """Validate if badge is a noble metal (LOL)."""

        if not BadgeTypeChoices.is_noble_metal(badge_type):
            raise serializers.ValidationError({"type": "Invalid Choice."})

    @staticmethod
    def validate_points_proficiency(points, proficiency):
        """Validate if both points & proficiency are present."""

        if not points:
            raise serializers.ValidationError({"points": "This field is required."})
        if not proficiency:
            raise serializers.ValidationError({"proficiency": "This field is required."})

    @staticmethod
    def validate_existing_badge(category, badge_type, proficiency=None, is_mml=False):
        """Validate present."""

        type_label = BadgeTypeChoices.get_choice(badge_type).label
        if is_mml:
            badge = Badge.objects.filter(category=category, type=badge_type)
            msg = f"Badge with this Type {type_label} already exists."
        else:
            badge = Badge.objects.filter(category=category, type=badge_type, proficiency=proficiency)
            proficiency_label = BadgeProficiencyChoices.get_choice(proficiency).label
            msg = f"Badge with this Type {type_label} & Proficiency {proficiency_label} already exists."
        if badge.exists():
            raise serializers.ValidationError({"type": msg})

    def validate(self, attrs):
        """Validate logic based on choice fields."""

        category, badge_type, proficiency = attrs["category"], attrs["type"], attrs.get("proficiency")
        points = attrs.get("points")

        match category:
            case BadgeCategoryChoices.video:
                if badge_type != BadgeTypeChoices.video:
                    raise serializers.ValidationError({"type": f"Invalid Choice. It must be {BadgeTypeChoices.video}"})
                self.validate_points_proficiency(points, proficiency)
                self.validate_existing_badge(category, badge_type, proficiency)
                self.validate_proficiency_against_points(category, badge_type, proficiency, points)
            case BadgeCategoryChoices.assessment:
                self.validate_badge_type(badge_type)
                self.validate_points_proficiency(points, proficiency)
                self.validate_existing_badge(category, badge_type, proficiency)
                self.validate_proficiency_against_points(category, badge_type, proficiency, points)
            case BadgeCategoryChoices.mml:
                self.validate_badge_type(badge_type)
                self.validate_existing_badge(category, badge_type, is_mml=True)
            case _:
                raise serializers.ValidationError({"type": "Invalid Choice."})
        return attrs

    def create(self, validated_data):
        """Populate necessary field while creating."""

        category, badge_type = validated_data["category"], validated_data["type"]
        from_range, to_range = None, None

        if category == BadgeCategoryChoices.mml:
            from_range = MML_BADGES_RANGE[badge_type]["from"]
            to_range = MML_BADGES_RANGE[badge_type]["to"]
        elif category == BadgeCategoryChoices.assessment:
            from_range = ASSESSMENT_BADGES_RANGE[badge_type]["from"]
            to_range = ASSESSMENT_BADGES_RANGE[badge_type]["to"]

        validated_data["from_range"] = from_range
        validated_data["to_range"] = to_range
        return super().create(validated_data)


class BadgeUpdateModelSerializer(BadgeCommonModelSerializer):
    """`Badge` model serializer for Update."""

    points = serializers.IntegerField()

    def validate(self, attrs):
        """Validate logic for points update."""

        points = attrs["points"]
        if self.instance.category in [BadgeCategoryChoices.video, BadgeCategoryChoices.assessment]:
            self.validate_proficiency_against_points(
                self.instance.category, self.instance.type, self.instance.proficiency, points
            )
        return attrs


class BadgeListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `Badge` model."""

    class Meta:
        model = Badge
        fields = [
            "id",
            "uuid",
            "category",
            "type",
            "proficiency",
            "points",
            "from_range",
            "to_range",
            "is_active",
            "created_at",
            "modified_at",
        ]


class BadgeActivityListSerializer(AppReadOnlyModelSerializer):
    """List & Retrieve serializer for `BadgeActivity` model."""

    badge = BadgeListSerializer()
    user = SimpleUserReadOnlyModelSerializer()

    class Meta:
        model = BadgeActivity
        fields = [
            "id",
            "uuid",
            "user",
            "badge",
            "points",
            "created_at",
            "modified_at",
        ]


class UserBadgeListSerializer(AppReadOnlyModelSerializer):
    """List serializer for `User` total badge count."""

    badges = serializers.SerializerMethodField()
    profile_picture = UserProfilePictureRetrieveSerializer()

    def get_badges(self, obj):
        """Get the total counts of user badges."""

        badges = {
            BadgeTypeChoices.video: obj.video_count,
            BadgeTypeChoices.silver: obj.silver_count,
            BadgeTypeChoices.gold: obj.gold_count,
            BadgeTypeChoices.platinum: obj.platinum_count,
            "total_points": obj.badges_points,
        }
        return badges

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "idp_id",
            "name",
            "email",
            "profile_picture",
            "badges",
        ]
