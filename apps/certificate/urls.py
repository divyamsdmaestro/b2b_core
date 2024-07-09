from django.urls import path

from .views.api import v1 as api_v1

V1_API_URL_PREFIX = "api/v1/certificate"

app_name = "certificate"

urlpatterns = [
    path(f"{V1_API_URL_PREFIX}/list/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/list/table-meta/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/detail/<int:pk>/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/cud/meta/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/cud/<int:pk>/meta/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/cud/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/cud/<int:pk>/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/sponsor/logo/upload/", api_v1.CertificateAPIView.as_view()),
    path(f"{V1_API_URL_PREFIX}/stamp/or/signature/upload/", api_v1.CertificateAPIView.as_view()),
]
