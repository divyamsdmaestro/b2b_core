from django.db.models import Q

from apps.common.serializers import get_app_read_only_serializer
from apps.common.views.api import AppAPIView
from apps.learning.models import Catalogue


class UserCatalogueMetaAPIView(AppAPIView):
    """Api view to show list of catalogues assigned to user."""

    def get(self, *args, **kwargs):
        """Returns the meta data."""

        return self.send_response(
            data={
                "catalogue": get_app_read_only_serializer(
                    meta_model=Catalogue,
                    meta_fields=["id", "name"],
                )(
                    Catalogue.objects.alive().filter(
                        Q(related_catalogue_relations__user_group__members__in=[self.get_user()])
                        | Q(related_catalogue_relations__user=self.get_user())
                    ),
                    many=True,
                ).data,
            }
        )
