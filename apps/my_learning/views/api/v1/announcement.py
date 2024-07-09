from django.db.models import Q

from apps.access_control.config import RoleTypeChoices
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.common.views.api.generic import get_upload_api_view
from apps.my_learning.config import AnnouncementTypeChoices
from apps.my_learning.models import Announcement, AnnouncementImageModel
from apps.my_learning.serializers.v1 import AnnouncementCUDModelSerializer, AnnouncementListModelSerializer

AnnouncementImageUploadAPIView = get_upload_api_view(meta_model=AnnouncementImageModel, meta_fields=["id", "image"])


class AnnouncementCUDApiViewSet(AppModelCUDAPIViewSet):
    """ViewSet for create, update & destroy Announcement."""

    serializer_class = AnnouncementCUDModelSerializer
    queryset = Announcement.objects.all()


class AnnouncementListApiViewSet(AppModelListAPIViewSet):
    """ViewSet to list Announcements."""

    serializer_class = AnnouncementListModelSerializer
    queryset = Announcement.objects.all()
    search_fields = ["title", "text", "type"]
    filterset_fields = ["type", "user", "user_group"]

    def get_queryset(self):
        """Overridden to filter the queryset based on the user role."""

        queryset = super().get_queryset()
        user = self.get_user()
        if not user.current_role:
            queryset = queryset.none()
        elif user.current_role.role_type == RoleTypeChoices.manager:
            queryset = queryset.filter(
                Q(type=AnnouncementTypeChoices.tenant_level) | Q(Q(user_group__manager=user) | Q(user=user))
            )
        elif user.current_role.role_type in [RoleTypeChoices.learner, RoleTypeChoices.author]:
            queryset = queryset.filter(
                Q(type=AnnouncementTypeChoices.tenant_level) | Q(Q(user_group__members=user) | Q(user=user))
            )
        return queryset
