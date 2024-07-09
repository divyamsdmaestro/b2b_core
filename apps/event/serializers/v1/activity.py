from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer, BaseIDNameSerializer
from apps.event.config import (
    ActivityTypeChoices,
    EndTypeChoices,
    RemainderChoices,
    RepeatEveryTypeChoices,
    RepeatTypeChoices,
    UserStatusChoices,
    UserVisibilityChoices,
    WeekDayChoices,
)
from apps.event.models import CalendarActivity
from apps.learning.models import AdvancedLearningPath, Course, LearningPath

EVENT_SUBTYPE_MODELS = {
    "course": Course,
    "learning_path": LearningPath,
    "advanced_learning_path": AdvancedLearningPath,
}


def repeat_on_string(repeat_type, custom_value=None):
    """Returns the string of week days."""

    if repeat_type == "custom" and custom_value:
        repeat_on = ",".join(custom_value)
    else:
        weekday_list = list(WeekDayChoices.values)
        if repeat_type == "every_weekday":
            weekday_list.remove("saturday")
            weekday_list.remove("sunday")
        repeat_on = ",".join(weekday_list)
    return repeat_on


class CalendarActivityCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Serializer class for calendar_activity."""

    repeat_on = serializers.MultipleChoiceField(choices=WeekDayChoices.choices, allow_null=True)
    automatically_decline_meetings = serializers.BooleanField(source="is_auto_decline", required=False)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = CalendarActivity
        fields = [
            "name",
            "activity_type",
            "activity_date",
            "from_time",
            "to_time",
            "automatically_decline_meetings",
            "repeat_type",
            "repeat_every_type",
            "repeat_occurrence_no",
            "repeat_on",
            "ends_type",
            "ends_on",
            "ends_after",
            "description",
            "user_status",
            "user_visibility",
            "notify",
        ]

    @staticmethod
    def update_repeat_on(validated_data):
        """Update the repeat_on value based on repeat_type."""

        if validated_data["repeat_type"] == "daily":
            validated_data["repeat_on"] = repeat_on_string("daily")
        elif validated_data["repeat_type"] == "every_weekday":
            validated_data["repeat_on"] = repeat_on_string("every_weekday")
        elif validated_data["repeat_type"] == "custom":
            validated_data["repeat_on"] = repeat_on_string("custom", validated_data["repeat_on"])
        return validated_data

    def validate_repeat_every_type(self, repeat_every_type):
        """Validate the repeat_every_type."""

        repeat_type = self.get_request().data.get("repeat_type", None)
        if repeat_type == "custom":
            if repeat_every_type is None:
                raise serializers.ValidationError("Please select at least one choice.")
        return repeat_every_type

    def validate_repeat_on(self, repeat_on):
        """Validate the repeat on field based on repeat_every_type"""

        repeat_every_type = self.get_request().data.get("repeat_every_type", None)
        if repeat_every_type == "week":
            if len(repeat_on) == 0:
                raise serializers.ValidationError("Please select at least one day.")
        return repeat_on

    def validate_ends_on(self, ends_on):
        """Validated the ends_on field based on ends_type."""

        ends_type = self.get_request().data.get("ends_type", None)
        if ends_type == "on":
            if not ends_on:
                raise serializers.ValidationError("Please specify the activity end date.")
        return ends_on

    def validate_ends_after(self, ends_after):
        """Validated the ends_after field based on ends_type."""

        ends_type = self.get_request().data.get("ends_type", None)
        if ends_type == "after":
            if not ends_after:
                raise serializers.ValidationError("Please specify the occurrence of activity.")
        return ends_after

    def create(self, validated_data):
        """Overridden to update necessary fields."""

        validated_data["user"] = self.get_user()
        validated_data = self.update_repeat_on(validated_data)
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """Overridden to update necessary fields."""

        validated_data["user"] = self.get_user()
        validated_data = self.update_repeat_on(validated_data)
        instance = super().update(instance, validated_data)
        return instance

    def get_dynamic_render_config(self):
        """Overridden to change the `repeat_on` field config."""

        render_config = super().get_dynamic_render_config()
        for data in render_config:
            if data["key"] == "repeat_on":
                data["type"] = "MultipleChoiceField"
        return render_config

    def get_meta(self) -> dict:
        """Returns the metadata."""

        return {
            "activity_type": self.serialize_dj_choices(ActivityTypeChoices.choices),
            "repeat_type": self.serialize_dj_choices(RepeatTypeChoices.choices),
            "repeat_every_type": self.serialize_dj_choices(RepeatEveryTypeChoices.choices),
            "repeat_on": self.serialize_dj_choices(WeekDayChoices.choices),
            "ends_type": self.serialize_dj_choices(EndTypeChoices.choices),
            "user_status": self.serialize_dj_choices(UserStatusChoices.choices),
            "user_visibility": self.serialize_dj_choices(UserVisibilityChoices.choices),
            "notify": self.serialize_dj_choices(RemainderChoices.choices),
        }

    def get_meta_initial(self):
        """Overridden to change the repeat_on field value."""

        initial_data = super().get_meta_initial()
        if initial_data["repeat_on"]:
            initial_data["repeat_on"] = initial_data["repeat_on"].split(",")
        return initial_data


class CalendarActivityListModelSerializer(AppReadOnlyModelSerializer):
    """Serializer class to list the CalendarActivities."""

    repeat_on = serializers.ListField(source="get_repeat_on")
    removed_dates = serializers.SerializerMethodField()
    automatically_decline_meetings = serializers.BooleanField(source="is_auto_decline", read_only=True)
    event_subtype_id = serializers.SerializerMethodField(read_only=True)

    def get_removed_dates(self, obj):
        """Returns a list of removed dates."""

        return obj.related_calendar_activity_trackers.filter(is_deleted=True).values_list("date", flat=True)

    def get_event_subtype_id(self, obj):
        """Returns the event sub type id with name"""

        if model := EVENT_SUBTYPE_MODELS.get(obj.event_subtype):
            event_subtype_obj = model.objects.get(pk=obj.event_subtype_id)
            return BaseIDNameSerializer(event_subtype_obj).data
        return {"id": obj.event_subtype_id, "name": obj.name}

    class Meta:
        model = CalendarActivity
        fields = [
            "id",
            "name",
            "activity_type",
            "activity_date",
            "from_time",
            "to_time",
            "automatically_decline_meetings",
            "repeat_type",
            "repeat_every_type",
            "repeat_occurrence_no",
            "repeat_on",
            "ends_type",
            "ends_on",
            "ends_after",
            "description",
            "user_status",
            "user_visibility",
            "notify",
            "removed_dates",
            "event_subtype",
            "event_subtype_id",
        ]
