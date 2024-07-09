from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import UserSkillOntologyRetrieveApiViewSet, UserSkillOntologyTrackerCreateApiViewSet

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/skill-ontology"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/tracker/create", UserSkillOntologyTrackerCreateApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", UserSkillOntologyRetrieveApiViewSet)

urlpatterns = [] + router.urls
