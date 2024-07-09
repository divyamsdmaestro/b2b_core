from django.conf import settings

from apps.common.communicator import get_request
from apps.common.views.api import AppAPIView, AppCreateAPIView, AppModelListAPIViewSet
from apps.tenant_service.middlewares import get_current_tenant_idp_id
from apps.virtutor.helpers import get_virtutor_trainer_details
from apps.virtutor.models import Trainer
from apps.virtutor.serializers.v1 import (
    AssignTrainerCreateModelSerializer,
    RemoveTrainerSerializer,
    TrainerListModelSerializer,
)


class MODTrainerListApiView(AppAPIView):
    """Api view to get the trainer's list form virtutor."""

    def get(self, request, *args, **kwargs):
        """Returns the trainer's list from virtutor."""

        skill_list = self.request.query_params.getlist("skill")
        url_path = settings.VIRTUTOR_CONFIG["trainer_list_url"] + f"?tenantId={get_current_tenant_idp_id()}"
        for skill in skill_list:
            url_path += f"&skills={skill}"
        success, data = get_request(
            service="VIRTUTOR",
            url_path=url_path,
        )
        if success and data["result"][0]["irisTrainerDetails"]:
            return self.send_response(data["result"][0]["irisTrainerDetails"])
        return self.send_error_response(data)


class AssignTrainerApiView(AppCreateAPIView):
    """Api view to assign trainers to course, lp & alp."""

    serializer_class = AssignTrainerCreateModelSerializer

    def post(self, request, *args, **kwargs):
        """Overridden to update the trainer details."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        trainer_details = validated_data.pop("trainer")
        for trainer in trainer_details:
            trainer_id = trainer.pop("trainer_id")
            trainer["skills"] = {"skills": trainer["skills"]}
            instance, created = Trainer.objects.update_or_create(trainer_id=trainer_id, defaults=trainer)
            if not created:
                validated_data["course"] = validated_data["course"] + list(instance.course.all())
                # validated_data["learning_path"] =
                # validated_data["learning_path"] + list(instance.learning_path.all())
                # validated_data["alp"] = validated_data["alp"] + list(instance.alp.all())
            instance.course.set(validated_data["course"])
            # instance.learning_path.set(validated_data["learning_path"])
            # instance.alp.set(validated_data["alp"])
        return self.send_response("Trainer(s) has been assigned successfully.")


class AssignTrainerMetaApiView(AppAPIView):
    """Api view to provide metadata."""

    serializer_class = AssignTrainerCreateModelSerializer

    def get(self, request, *args, **kwargs):
        """Returns the metadata."""

        return self.send_response(self.serializer_class().get_meta_for_create())


class AssignedTrainerListApiView(AppModelListAPIViewSet):
    """Api view list the trainers."""

    serializer_class = TrainerListModelSerializer
    queryset = Trainer.objects.all()
    filterset_fields = ["course", "learning_path", "alp"]


class RemoveTrainerApiView(AppAPIView):
    """Remove the trainer from course, lp or alp."""

    serializer_class = RemoveTrainerSerializer

    def post(self, request, *args, **kwargs):
        """Remove the course, lp & alp from trainer instance."""

        validated_data = self.get_valid_serializer().validated_data
        trainer = validated_data["trainer"]
        trainer.course.remove(validated_data["course"])
        trainer.learning_path.remove(validated_data["learning_path"])
        trainer.alp.remove(validated_data["alp"])

        return self.send_response("Trainer removed successfully.")


class TrainerDetailApiView(AppAPIView):
    """Api view to provide trainer details."""

    def get(self, request, *args, **kwargs):
        """Returns the virtutor assigned trainer details."""

        trainer_id = kwargs.get("trainer_id")
        idp_token = request.headers.get("idp-token", None) or request.headers.get("sso-token")
        success, trainer_data = get_virtutor_trainer_details(auth_token=idp_token, trainer_id=trainer_id)
        if not success:
            return self.send_error_response(trainer_data)
        return self.send_response(trainer_data["result"]["irisTrainerRecordDetails"][0])
