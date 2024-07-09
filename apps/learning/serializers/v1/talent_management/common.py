from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppSpecificImageFieldSerializer,
    AppWriteOnlyModelSerializer,
)
from apps.learning.models import Catalogue
from apps.learning.serializers.v1 import talent_managements


class CommonTalentManagementCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Common CUD model serializer for ctegory, role, skill."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        fields = [
            "name",
            "image",
            "description",
            "is_draft",
            "is_archive",
            "is_active",
            "is_popular",
            "is_recommended",
        ]

    def validate_name(self, name):
        """Overridden to validate the name with lower case."""

        existing_objs = self.Meta.model.objects.alive().filter(name__iexact=name)
        if self.instance:
            existing_objs = existing_objs.exclude(id=self.instance.id)
        if existing_objs.first():
            raise serializers.ValidationError("This field must be unique.")
        return name


class CommonTalentManagementListSerializer(AppReadOnlyModelSerializer):
    """Common serializer to list category, skill & role."""

    user_favourite = serializers.SerializerMethodField()
    no_of_course = serializers.SerializerMethodField()
    no_of_lp = serializers.SerializerMethodField()
    no_of_alp = serializers.SerializerMethodField()
    image = AppSpecificImageFieldSerializer(read_only=True)

    def get_user_favourite(self, obj):
        """Returns True if the category is marked as a favorite by user, otherwise False."""

        user_favourite = obj.related_user_favourites.filter(user=self.get_user()).first()
        return {"id": user_favourite.id if user_favourite else None, "is_favourite": bool(user_favourite)}

    def get_no_of_course(self, obj):
        """Returns the number of courses for the selected catalogue or returns overall count."""

        if catalogue_id := self.get_request().query_params.get("catalogue_id"):
            catalogue = get_object_or_404(Catalogue, id=catalogue_id)
            talent_management = talent_managements[obj.__class__.__name__]
            return catalogue.course.filter(**{talent_management: obj}).count()
        return obj.no_of_course

    def get_no_of_lp(self, obj):
        """Returns the number of lp for the selected catalogue or returns overall count."""

        if catalogue_id := self.get_request().query_params.get("catalogue_id"):
            catalogue = get_object_or_404(Catalogue, id=catalogue_id)
            talent_management = talent_managements[obj.__class__.__name__]
            return catalogue.learning_path.filter(**{talent_management: obj}).count()
        return obj.no_of_lp

    def get_no_of_alp(self, obj):
        """Returns the number of alp for the selected catalogue or returns overall count."""

        if catalogue_id := self.get_request().query_params.get("catalogue_id"):
            catalogue = get_object_or_404(Catalogue, id=catalogue_id)
            talent_management = talent_managements[obj.__class__.__name__]
            return catalogue.advanced_learning_path.filter(**{talent_management: obj}).count()
        return obj.no_of_alp

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = [
            "id",
            "name",
            "image",
            "description",
            "created_at",
            "no_of_course",
            "no_of_lp",
            "no_of_alp",
            "is_active",
            "is_popular",
            "is_recommended",
            "user_favourite",
        ]
