from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.learning.views.api.v1 import (
    CatalogueCloneApiView,
    CatalogueCUDApiViewSet,
    CatalogueListApiViewSet,
    CatalogueLockStatusUpdateApiViewSet,
    CatalogueRelationCUDApiViewSet,
    CatalogueRelationListApiView,
    CatalogueRetrieveApiViewSet,
    UserCatalogueListApiViewSet,
)

app_name = "catalogue"
API_URL_PREFIX = "api/v1/catalogue"

router = AppSimpleRouter()

# Catalogue Api's
router.register(f"{API_URL_PREFIX}/cud", CatalogueCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/list", CatalogueListApiViewSet)
router.register(f"{API_URL_PREFIX}/view-detail", CatalogueRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/lock/status/update", CatalogueLockStatusUpdateApiViewSet)
router.register(f"{API_URL_PREFIX}/relation/cud", CatalogueRelationCUDApiViewSet)
router.register("api/v1/user/catalogue/list", UserCatalogueListApiViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}/relation/list/", CatalogueRelationListApiView.as_view(), name="catalogue-relation-list"),
    path(f"{API_URL_PREFIX}/clone/", CatalogueCloneApiView.as_view(), name="catalogue-clone"),
] + router.urls
