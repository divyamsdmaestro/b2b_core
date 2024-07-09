import os

from django.core.files.storage import default_storage
from moviepy import editor as video_editor

from apps.common.tasks import BaseAppTask
from apps.learning.config import BaseResourceTypeChoices, BaseUploadStatusChoices
from apps.tenant_service.middlewares import get_current_db_name


class ResourceUploadTask(BaseAppTask):
    """Task to upload the resource files and add the url."""

    def run(self, resource_file_path, filename, db_name, resource_pk, learning_type, resource_type, **kwargs):
        """Run handler."""

        # TODO: Need to implement duration calculation

        from apps.learning.models import (
            AdvancedLearningPathResource,
            AssignmentResource,
            CourseResource,
            CourseSubModule,
            LearningPathResource,
            SkillTravellerResource,
        )

        resource_model = {
            "course": CourseResource,
            "sub_module": CourseSubModule,
            "learning_path": LearningPathResource,
            "advanced_learning_path": AdvancedLearningPathResource,
            "skill_traveller": SkillTravellerResource,
            "assignment": AssignmentResource,
        }
        self.switch_db(db_name)
        resource_instance = resource_model[learning_type].objects.get(pk=resource_pk)
        resource_instance.upload_status = BaseUploadStatusChoices.in_progress
        resource_instance.save()
        if learning_type == "sub_module":
            learning_obj = resource_instance
        else:
            learning_obj = getattr(resource_instance, learning_type)
        self.logger.info(f"Got ResourceUpload Task For : {learning_obj.name} on {get_current_db_name()}")

        old_file_path = resource_instance.file_url
        try:
            # upload the file to default storage
            upload_dir = os.path.join(f"files/{db_name}/{learning_type}/resource", filename)
            resource_file = open(resource_file_path, "rb")
            uploaded_file = default_storage.save(upload_dir, resource_file)
            if resource_type == BaseResourceTypeChoices.video:
                video = video_editor.VideoFileClip(resource_file_path)
                resource_instance.duration = int(video.duration)
                video.close()
            # update the file_url & status to resource instance
            resource_instance.file_url = default_storage.url(uploaded_file)
            resource_instance.upload_status = BaseUploadStatusChoices.completed
            resource_instance.save()
            if old_file_path:
                default_storage.delete(old_file_path)
            # remove the resource file from project folder
            resource_file.close()
            if learning_type == "sub_module":
                resource_instance.duration_update()
        except Exception:  # noqa
            resource_instance.upload_status = BaseUploadStatusChoices.failed
            resource_instance.save()
        try:
            os.remove(resource_file_path)
        except FileNotFoundError:
            pass
        return True
