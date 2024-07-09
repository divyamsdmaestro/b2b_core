from rest_framework.decorators import action

from apps.common.helpers import get_sorting_meta
from apps.common.views.api import (
    AppModelListAPIViewSet,
    CatalogueFilterMixin,
    CustomQuerysetFilterMixin,
    SortingMixin,
    UserGroupFilterMixin,
)
from apps.learning.helpers import BaseLearningSkillRoleFilter


class BaseLearningSkillRoleListApiViewSet(
    SortingMixin, CatalogueFilterMixin, UserGroupFilterMixin, CustomQuerysetFilterMixin, AppModelListAPIViewSet
):
    """Api viewset to list courses."""

    filterset_class = BaseLearningSkillRoleFilter
    search_fields = ["name", "code"]

    @action(detail=False)
    def meta(self, request, *args, **kwargs):
        """Filter Meta for Frontend."""

        sorting_options = self.get_sorting_options(
            {
                "-modified_at": "Accessed Recently",
                "end_date": "Nearing Deadline",
            }
        )
        data = self.serializer_class().get_filter_meta()
        data["sort_by"] = get_sorting_meta(sorting_options)
        return self.send_response(data)
