from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import SkillOntologyCreateApiViewSet

app_name = "skill_ontology"
API_URL_PREFIX = "api/v1/skill-ontology"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/create", SkillOntologyCreateApiViewSet)

urlpatterns = [] + router.urls
