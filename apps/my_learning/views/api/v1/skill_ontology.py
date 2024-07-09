from apps.common.views.api import AppModelCreateAPIViewSet, AppModelRetrieveAPIViewSet
from apps.learning.models import SkillOntology
from apps.my_learning.models.tracker.skill_ontology import UserSkillOntologyTracker
from apps.my_learning.serializers.v1 import (
    UserSkillOntologyRetrieveSerializer,
    UserSkillOntologyTrackerCreateSerializer,
)


class UserSkillOntologyTrackerCreateApiViewSet(AppModelCreateAPIViewSet):
    """Api view to create skill ontology tracker."""

    serializer_class = UserSkillOntologyTrackerCreateSerializer
    queryset = UserSkillOntologyTracker.objects.all()


class UserSkillOntologyRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Api view to retrieve skill ontology."""

    serializer_class = UserSkillOntologyRetrieveSerializer
    queryset = SkillOntology.objects.all()
