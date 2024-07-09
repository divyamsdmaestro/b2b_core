from apps.common.routers import AppSimpleRouter
from apps.my_learning.views.api.v1 import (
    FeedbackResponseCreateApiViewset,
    UserFeedbackResponseListApiViewset,
    UserFeedbackTemplateListApiViewset,
)

app_name = "my_learning"
API_URL_PREFIX = "api/v1/my-learning/feedback"

router = AppSimpleRouter()

router.register(f"{API_URL_PREFIX}/list", UserFeedbackTemplateListApiViewset)
router.register(f"{API_URL_PREFIX}/detail", UserFeedbackResponseListApiViewset)
router.register(f"{API_URL_PREFIX}/create", FeedbackResponseCreateApiViewset)

urlpatterns = [] + router.urls
