"""
Note:
    If more tenant requests for custom user onboard API then make sub-folders based on tenant name
    and add custom serializers instead of this common serializer.
"""
from rest_framework import serializers

from apps.access.models import User, UserDetail
from apps.common.serializers import AppSerializer


class CustomUserDetailCommonSerializer(AppSerializer):
    """Serializer class for tenant `UserDetail`."""

    user_grade = serializers.CharField(allow_null=True, required=False)
    employment_start_date = serializers.DateField(allow_null=True, required=False)
    job_title = serializers.CharField(allow_null=True, required=False)
    job_description = serializers.CharField(allow_null=True, required=False)
    department_code = serializers.CharField(allow_null=True, required=False)
    department_title = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.IntegerField(allow_null=True, required=False)
    manager_name = serializers.CharField(allow_null=True, required=False)
    manager_email = serializers.EmailField(allow_null=True, required=False)
    manager_two_email = serializers.EmailField(allow_null=True, required=False)
    manager_three_email = serializers.EmailField(allow_null=True, required=False)
    business_unit_name = serializers.CharField(allow_null=True, required=False)
    employment_status = serializers.CharField(allow_null=True, required=False)
    is_onsite_user = serializers.BooleanField(default=False, required=False)


class CustomUserDetailCreateSerializer(CustomUserDetailCommonSerializer):
    """Serializer class for tenant `UserDetail`."""

    employee_id = serializers.CharField(allow_null=True, required=False)

    def validate_employee_id(self, employee_id):
        """Validate if employee_id already exists."""

        if UserDetail.objects.filter(employee_id=employee_id).exists():
            raise serializers.ValidationError("This Employee ID is already taken.")
        return employee_id


class CustomUserOnboardSerializer(AppSerializer):
    """Create serializer class for tenant `User`."""

    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=True)
    user_id_number = serializers.CharField()
    user_details = CustomUserDetailCreateSerializer()

    def validate(self, attrs):
        """Validate if User already exists."""

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "User already exists with this email."})
        if UserDetail.objects.filter(user_id_number=attrs["user_id_number"]).exists():
            raise serializers.ValidationError({"user_id_number": "This User ID is already taken."})
        return attrs


class CustomUserStatusSerializer(AppSerializer):
    """User account toggle serializer."""

    user_id_number = serializers.CharField()
    is_active = serializers.BooleanField()

    def validate(self, attrs):
        """Validate User exists."""

        user_detail = UserDetail.objects.filter(user_id_number=attrs["user_id_number"]).first()
        if not user_detail:
            raise serializers.ValidationError({"user_id_number": "Invalid User Id."})
        attrs["user"] = user_detail.user
        return attrs


class CustomUserUpdateSerializer(AppSerializer):
    """Update serializer class for tenant `User`."""

    user_id_number = serializers.CharField()
    first_name = serializers.CharField(allow_null=True, required=False)
    last_name = serializers.CharField(allow_null=True, required=False)
    user_details = CustomUserDetailCommonSerializer(required=False)

    def validate(self, attrs):
        """Validate User Exists."""

        user_detail = UserDetail.objects.filter(user_id_number=attrs["user_id_number"]).first()
        if not user_detail:
            raise serializers.ValidationError({"user_id_number": "Invalid User Id."})
        attrs["user"] = user_detail.user
        return attrs
