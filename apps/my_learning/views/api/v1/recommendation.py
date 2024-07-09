from django.db.models import Q

from apps.common.communicator import get_request
from apps.common.views.api.base import AppAPIView
from apps.learning.models import Course
from apps.learning.serializers.v1 import CourseListModelSerializer
from apps.tenant_service.middlewares import get_current_tenant_details
from config.settings.base import DEVONE_CONFIG

RESOURCE_MODELS = {
    "course": Course,
}

RESOURCE_SERIALIZERS = {
    "course": CourseListModelSerializer,
}


class LearningRecommendationAPIView(AppAPIView):
    """Api view to get learning recommendations."""

    def get(self, *args, **kwargs):
        """Handle on get."""

        user = self.get_user()
        tenant_id = get_current_tenant_details()["id"]
        success, data = get_request(
            service=None,
            host=DEVONE_CONFIG["host"],
            url_path=DEVONE_CONFIG["recommendation_url"],
            params={"tenant": tenant_id, "user": user.id},
        )
        if not success:
            return self.send_error_response(data=data)
        response = {"course": []}
        if tenant_id == 861:
            # TODO: Hardcoded this for demoiiht tenant as per dakshans context. Need to remove this.
            user_group = user.related_user_groups.all()
            courses = Course.objects.filter(
                Q(related_learning_catalogues__related_catalogue_relations__user_group__in=user_group)
                | Q(related_learning_catalogues__related_catalogue_relations__user=user)
                | Q(related_enrollments__user=user)
                | Q(related_enrollments__user_group__in=user_group)
            ).distinct()
            response["course"] = RESOURCE_SERIALIZERS["course"](courses, many=True).data
        else:
            for data in data:
                resource_type = data["ResourceType"].lower()
                if len(response[resource_type]) > 4:
                    continue
                if data["ModelOutput"]:
                    if obj := RESOURCE_MODELS[resource_type].objects.alive().filter(id=data["ResourceId"]).first():
                        response[resource_type].append(RESOURCE_SERIALIZERS[resource_type](obj).data)
        return self.send_response(response)
