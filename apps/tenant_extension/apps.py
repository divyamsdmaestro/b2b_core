from django.apps import AppConfig


class TenantExtensionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenant_extension"
