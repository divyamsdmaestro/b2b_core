from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

admin.site.site_header = "Super Admin"
admin.site.site_title = "Super Admin Portal"
admin.site.index_title = "Welcome to Techademy Admin portal."

urlpatterns = [
    path("", include("apps.common.urls")),
    path("", include("apps.access.urls")),
    path("", include("apps.tenant.urls")),
    path("", include("apps.access_control.urls")),
    path("", include("apps.learning.urls")),
    path("", include("apps.my_learning.urls")),
    path("", include("apps.certificate.urls")),
    path("", include("apps.meta.urls")),
    path("", include("apps.forum.urls")),
    path("", include("apps.leaderboard.urls")),
    path("", include("apps.event.urls")),
    path("", include("apps.virtutor.urls")),
    path("", include("apps.mailcraft.urls")),
    path("", include("apps.webhook.urls")),
    path("", include("apps.notification.urls")),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.tenant_extension.urls")),  # Always keep at last third.
    path("", include("apps.techademy_one.urls")),  # Always keep at last second.
    path(settings.ADMIN_URL, admin.site.urls),  # Always keep at last.
]

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()
