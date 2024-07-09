from datetime import datetime, timedelta

from django.db.models import Q

from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.common.views.api import AppAPIView, AppModelCUDAPIViewSet
from apps.event.config import CalendarEventTypeChoices
from apps.event.models import CalendarActivity, CalendarActivityTrackingModel
from apps.event.serializers.v1 import CalendarActivityCUDModelSerializer, CalendarActivityListModelSerializer


class CalendarActivityCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to create, edit & delete the calendar activity."""

    serializer_class = CalendarActivityCUDModelSerializer
    queryset = CalendarActivity.objects.all()


class CalendarActivityListApiView(AppAPIView):
    """Api view to list the calendar activities."""

    serializer_class = CalendarActivityListModelSerializer

    def get(self, request, *args, **kwargs):
        """Returns the calendar activities."""

        user = self.get_user()
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        event_subtype = request.query_params.get("event_subtype")
        event_subtype_id = request.query_params.get("event_subtype_id")
        if not month or not year:
            return self.send_error_response("No month or year specified.")
        month, year = int(month), int(year)
        queryset = CalendarActivity.objects.filter(
            Q(activity_date__month=month, activity_date__year=year) | Q(ends_on__month=month, ends_on__year=year)
        ).filter(user=user)
        if event_subtype and event_subtype_id:
            if event_subtype == CalendarEventTypeChoices.course:
                queryset = queryset.filter(
                    Q(event_subtype=event_subtype) | Q(event_subtype=CalendarEventTypeChoices.session),
                    event_subtype_id=event_subtype_id,
                )
            else:
                queryset = queryset.filter(event_subtype=event_subtype, event_subtype_id=event_subtype_id)
        activity_data = self.serializer_class(queryset, many=True).data
        expanded_activities = self.expand_activities(activity_data)
        return self.send_response({"activity_data": expanded_activities})

    def expand_activities(self, calendar_activities):
        """Expand activities based on activity_date and ends_on."""

        expanded_activities = []
        for activity in calendar_activities:
            activity_date = activity["activity_date"]
            ends_on = activity["ends_on"]
            if activity_date and ends_on:
                current_date = datetime.strptime(activity_date, "%Y-%m-%d")
                ends_on = datetime.strptime(ends_on, "%Y-%m-%d")
                while current_date <= ends_on:
                    expanded_activity = self.get_activities_data(activity, current_date, ends_on)
                    expanded_activities.append(expanded_activity)
                    current_date += timedelta(days=1)
            else:
                # If no ends_on, just include the original activity
                expanded_activities.append(activity)

        return expanded_activities

    def get_activities_data(self, activity, current_date, ends_on):
        """Create an expanded activity data."""

        return {
            "id": activity["id"],
            "name": activity["name"],
            "activity_type": activity["activity_type"],
            "activity_date": current_date.strftime("%Y-%m-%d"),
            "from_time": activity["from_time"],
            "to_time": activity["to_time"],
            "automatically_decline_meetings": activity["automatically_decline_meetings"],
            "repeat_type": activity["repeat_type"],
            "repeat_every_type": activity["repeat_every_type"],
            "repeat_occurrence_no": activity["repeat_occurrence_no"],
            "repeat_on": activity["repeat_on"],
            "ends_type": activity["ends_type"],
            "ends_on": ends_on.strftime("%Y-%m-%d"),
            "ends_after": activity["ends_after"],
            "description": activity["description"],
            "user_status": activity["user_status"],
            "user_visibility": activity["user_visibility"],
            "notify": activity["notify"],
            "removed_dates": activity["removed_dates"],
            "event_subtype": activity["event_subtype"],
            "event_subtype_id": activity["event_subtype_id"],
        }


class CalendarActivityDeleteApiView(AppAPIView):
    """Api view to delete events."""

    class _Serializer(AppWriteOnlyModelSerializer):
        """Serializer class to delete events."""

        class Meta(AppWriteOnlyModelSerializer.Meta):
            model = CalendarActivityTrackingModel
            fields = [
                "activity",
                "date",
            ]

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Delete the event."""

        valid_data = self.get_valid_serializer().validated_data
        if self.get_user() != valid_data["activity"].user:
            return self.send_error_response("Unauthorized user")
        valid_data["user"] = self.get_user()
        valid_data["is_deleted"] = True
        self.serializer_class().create(valid_data)
        return self.send_response("Deleted")
