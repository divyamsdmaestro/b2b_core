from apps.common.views.api import AppModelCreateAPIViewSet
from apps.learning.models import SkillOntology
from apps.learning.serializers.v1 import SkillOntologyCreateSerializer


class SkillOntologyCreateApiViewSet(AppModelCreateAPIViewSet):
    """Api view to create skill ontology."""

    queryset = SkillOntology.objects.all()
    serializer_class = SkillOntologyCreateSerializer
