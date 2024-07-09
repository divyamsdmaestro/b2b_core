from apps.common.routers import AppSimpleRouter
from apps.mailcraft.views.api import v1 as api_v1

V1_API_URL_PREFIX = "api/v1/mail/template"

app_name = "mailcraft"

router = AppSimpleRouter()
router.register(f"{V1_API_URL_PREFIX}/list", api_v1.MailTemplateListAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/detail", api_v1.MailTemplateRetrieveAPIViewSet)
router.register(f"{V1_API_URL_PREFIX}/cud", api_v1.MailTemplateCUAPIViewSet)


urlpatterns = [] + router.urls
