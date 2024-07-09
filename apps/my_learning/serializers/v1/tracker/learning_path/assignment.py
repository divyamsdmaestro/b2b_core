from django.db.models import Q
from rest_framework import serializers

from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.learning.config import CommonLearningAssignmentTypeChoices, EvaluationTypeChoices
from apps.learning.models import LPAssignment
from apps.learning.serializers.v1 import LPAssignmentListModelSerializer
from apps.my_learning.models import AssignmentTracker


class UserLPAssignmentListSerializer(LPAssignmentListModelSerializer):
    """LP assignment list serializer"""

    tracker_detail = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    def get_tracker_detail(self, obj):
        """Returns the tracker details of assignment."""

        tracker = obj.assignment.related_assignment_trackers.filter(user=self.get_user()).first()
        return (
            read_serializer(
                meta_model=AssignmentTracker,
                meta_fields=[
                    "id",
                    "assignment",
                    "enrollment",
                    "progress",
                    "completed_duration",
                    "allowed_attempt",
                    "available_attempt",
                    "last_accessed_on",
                    "is_pass",
                    "is_completed",
                    "completion_date",
                ],
            )(tracker).data
            if tracker
            else None
        )

    def get_is_locked(self, obj):
        """Returns if the assignment is locked or not."""

        user = self.get_user()
        tracker = obj.assignment.related_assignment_trackers.filter(user=user).first()
        lp_tracker = self.context.get("lp_tracker", None)
        if not lp_tracker:
            return True
        if (
            (lp_tracker and lp_tracker.is_completed)
            or tracker
            or not lp_tracker.learning_path.is_dependencies_sequential
            or obj.assignment.evaluation_type == EvaluationTypeChoices.non_evaluated
        ):
            return False
        if obj.type == CommonLearningAssignmentTypeChoices.dependent_assignment:
            course_tracker = user.related_user_course_trackers.filter(course=obj.lp_course.course).first()
            previous_assignment_objs = LPAssignment.objects.filter(
                lp_course=obj.lp_course, sequence__lt=obj.sequence
            ).values_list("assignment_id", flat=True)
            previous_assignment_qs = user.related_assignment_trackers.filter(
                assignment_id__in=previous_assignment_objs,
                assignment__evaluation_type=EvaluationTypeChoices.evaluated,
            )
            uncompleted_previous_assignment = previous_assignment_qs.filter(is_completed=False)
            if (
                not course_tracker
                or not course_tracker.is_completed
                or previous_assignment_qs.count() != previous_assignment_objs.count()
                or uncompleted_previous_assignment
            ):
                return True
            return False
        else:
            previous_course_objs = obj.learning_path.related_learning_path_courses.all()
            previous_course_qs = user.related_user_course_trackers.filter(
                course_id__in=previous_course_objs.values_list("course__id", flat=True)
            )
            uncompleted_previous_course = previous_course_qs.filter(is_completed=False).first()
            previous_assignment_objs = LPAssignment.objects.filter(
                learning_path=obj.learning_path,
                sequence__lt=obj.sequence,
                assignment__evaluation_type=EvaluationTypeChoices.evaluated,
            ).values_list("assignment_id", flat=True)
            previous_course_assignment_objs = LPAssignment.objects.filter(lp_course__in=previous_course_objs)
            previous_assignment_qs = user.related_assignment_trackers.filter(
                Q(assignment_id__in=previous_course_assignment_objs) | Q(assignment_id__in=previous_assignment_objs)
            )
            uncompleted_previous_assignment = previous_assignment_qs.filter(is_completed=False).first()
            if (
                uncompleted_previous_course
                or uncompleted_previous_assignment
                or previous_course_qs.count() != previous_course_objs.count()
                or previous_assignment_qs.count()
                != previous_assignment_objs.count() + previous_course_assignment_objs.count()
            ):
                return True
            return False

    class Meta(LPAssignmentListModelSerializer.Meta):
        fields = LPAssignmentListModelSerializer.Meta.fields + ["tracker_detail", "is_locked"]