from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.webhook.views.api.v1 import CAWecpWebhookApiView, YakshaResultWebhookAPIView

app_name = "webhook"
API_URL_PREFIX = "api/v1/webhook"

router = AppSimpleRouter()

urlpatterns = [
    path("api/v1/webhooks/assessment/result/hook/", CAWecpWebhookApiView.as_view()),
    # path(f"{API_URL_PREFIX}/assessment/wecp/result/", CAWecpWebhookApiView.as_view()),
    path(f"{API_URL_PREFIX}/assessment/yaksha/result/", YakshaResultWebhookAPIView.as_view()),
]
