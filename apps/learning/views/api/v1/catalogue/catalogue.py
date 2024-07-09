from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from apps.access_control.config import RoleTypeChoices
from apps.access_control.models import UserGroup
from apps.common.serializers import AppReadOnlyModelSerializer, AppSerializer, AppUpdateModelSerializer
from apps.common.views.api import (
    AppAPIView,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    AppModelUpdateAPIViewSet,
)
from apps.learning.models import Catalogue, CatalogueRelation
from apps.learning.serializers.v1 import (
    CatalogueCUDModelSerializer,
    CatalogueListModelSerializer,
    CatalogueRelationCUDModelSerializer,
    CatalogueRelationListModelSerializer,
    CatalogueRetrieveSerializer,
)


class CatalogueCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api view to create, edit & delete the catalogue."""

    queryset = Catalogue.objects.alive()
    serializer_class = CatalogueCUDModelSerializer


class CatalogueListApiViewSet(AppModelListAPIViewSet):
    """Api view to list the Catalogue."""

    queryset = Catalogue.objects.alive().order_by("created_at")
    serializer_class = CatalogueListModelSerializer
    search_fields = ["name"]
    all_table_columns = {
        "name": "Catalogue Name",
        "modified_at": "Last Modified On",
        "created_at": "Date Of Creation",
        "created_by": "Created By",
        "no_of_course": "Courses",
        "no_of_lp": "Learning Paths",
        "no_of_alp": "Custom Learning Paths",
        "no_of_st": "Skill Travellers",
        "no_of_tp": "Playgrounds",
        "no_of_tpg": "Playground Groups",
        "no_of_assignment": "Assignments",
        "no_of_assignment_group": "Assignment Groups",
    }

    def get_queryset(self):
        """Based on role filter the queryset returned."""

        queryset = super().get_queryset()
        user = self.get_user()
        if not user.current_role:
            return queryset.none()
        if user.current_role.role_type == RoleTypeChoices.admin:
            return queryset
        elif user.current_role.role_type == RoleTypeChoices.manager:
            return queryset.filter(related_catalogue_relations__user_group__in=UserGroup.objects.filter(manager=user))
        return queryset.filter(
            Q(related_catalogue_relations__user_group__in=user.related_user_groups.all())
            | Q(related_catalogue_relations__user=user)
        )


class CatalogueRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Viewset to retrieve the catalogue details."""

    serializer_class = CatalogueRetrieveSerializer
    queryset = Catalogue.objects.alive()


class CatalogueLockStatusUpdateApiViewSet(AppModelUpdateAPIViewSet):
    """Api viewset to update the lock status of the catalogue."""

    class _Serializer(AppUpdateModelSerializer):
        """Serializer class for the same viewset."""

        class Meta(AppUpdateModelSerializer.Meta):
            model = Catalogue
            fields = [
                "is_locked",
                "is_self_enroll_enabled",
            ]

    serializer_class = _Serializer
    queryset = Catalogue.objects.alive()


class CatalogueRelationListApiView(AppAPIView):
    """List api view for catalogue relations."""

    serializer_class = CatalogueRelationListModelSerializer

    def get(self, request, *args, **kwargs):
        """Returns the list of catalogue relations."""

        catalogue = request.query_params.get("catalogue")
        ccms_id = request.query_params.get("ccms_id")
        if catalogue:
            instance = get_object_or_404(Catalogue, pk=catalogue)
            queryset = CatalogueRelation.objects.filter(catalogue=instance.id).first()
        else:
            queryset = CatalogueRelation.objects.filter(ccms_id=ccms_id).first()
        return self.send_response(self.serializer_class(queryset).data if queryset else None)


class CatalogueRelationCUDApiViewSet(AppModelCUDAPIViewSet):
    """CUD Api viewset for catalogue relations."""

    serializer_class = CatalogueRelationCUDModelSerializer
    queryset = CatalogueRelation.objects.all()


class UserCatalogueListApiViewSet(AppModelListAPIViewSet):
    """Api view to return the catalogues based on catalogue relation."""

    class _Serializer(AppReadOnlyModelSerializer):
        """Serializer class for retrieve the details of a catalogue."""

        catalogue = CatalogueListModelSerializer(read_only=True)

        class Meta(AppReadOnlyModelSerializer.Meta):
            model = CatalogueRelation
            fields = ["catalogue", "ccms_id", "is_ccms_obj"]

        def to_representation(self, instance):
            """Overridden to return the ccms detail if it was a ccms obj."""

            from apps.learning.helpers import get_ccms_retrieve_details

            results = super().to_representation(instance)
            if instance.is_ccms_obj:
                success, data = get_ccms_retrieve_details(
                    learning_type="catalogue",
                    instance_id=str(instance.ccms_id),
                    request={"headers": dict(self.get_request().headers)},
                )
                if success:
                    results["ccms_id"] = data["data"]
            return results

    serializer_class = _Serializer
    queryset = CatalogueRelation.objects.all().order_by("created_at")

    def get_queryset(self):
        """Returns the instance based on role."""

        queryset = super().get_queryset()
        user = self.get_user()
        if not user.current_role:
            return queryset.none()
        elif user.current_role.role_type == RoleTypeChoices.manager:
            return queryset.filter(user_group__in=UserGroup.objects.filter(manager=user))
        # TODO: Need to clear this filter issue
        return (
            queryset.filter(Q(user_group__in=user.related_user_groups.all()) | Q(user=user))
            .exclude(catalogue__is_locked=True)
            .distinct()
        )


class CatalogueCloneApiView(AppAPIView):
    """Api view to clone the given catalogue."""

    class _Serializer(AppSerializer):
        """Serializer class for the same."""

        catalogue = serializers.PrimaryKeyRelatedField(queryset=Catalogue.objects.alive())

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        """Clone the catalogue logic."""

        serializer = self.get_valid_serializer()
        catalogue = serializer.validated_data["catalogue"]
        clone_details = catalogue.clone()
        return self.send_response(data=clone_details)
