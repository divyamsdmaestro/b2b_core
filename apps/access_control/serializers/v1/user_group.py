from rest_framework import serializers

from apps.access.models import User
from apps.access_control.models import UserGroup
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer


class UserGroupModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for `UserGroup` model."""

    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.alive(), many=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserGroup
        fields = ["name", "group_id", "members", "manager"]

    def validate(self, attrs):
        """
        Validate if manager himself in not in the members list. As per Dharshan's KT (IIHT),
        manager should not be in the members list.
        """

        members = attrs["members"]
        manager = attrs["manager"]
        if manager in members:
            raise serializers.ValidationError({"manager": "Manager should not be in the members list."})
        for member in members:
            groups = member.related_user_groups.all()
            if self.instance:
                groups = groups.exclude(id=self.instance.id)
            if groups:
                raise serializers.ValidationError(
                    {"members": f"A Group member {member.name} is already in an another group."}
                )
        return attrs

    def get_meta_initial(self):
        """Overridden to add the details of members and manager in initial data."""

        data = super().get_meta_initial()
        data.update(
            {
                "members": BaseIDNameSerializer(self.instance.members.all(), many=True).data,
                "manager": BaseIDNameSerializer(self.instance.manager).data if self.instance.manager else None,
            }
        )
        return data


class UserGroupReadOnlySerializer(AppReadOnlyModelSerializer):
    """Read Only Serializer for `User Group` Model"""

    manager = BaseIDNameSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserGroup
        fields = ["id", "name", "manager", "manager_email"]
