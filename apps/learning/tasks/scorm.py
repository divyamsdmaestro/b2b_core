import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

from django.core.files.storage import default_storage

from apps.common.config import DEFAULT_SCORM_OTHER_VERSION_NS, DEFAULT_SCORM_STANDARD_VERSION_NS
from apps.common.tasks import BaseAppTask
from apps.tenant_service.middlewares import get_current_db_name


class ScormUploadTask(BaseAppTask):
    """Task to upload the scorm file."""

    def run(self, file_path, file_name, db_name, scorm_pk, **kwargs):
        """Run handler."""

        from apps.learning.config import BaseUploadStatusChoices
        from apps.learning.models import Scorm

        self.switch_db(db_name)
        scorm_instance = Scorm.objects.get(pk=scorm_pk)
        upload_status = BaseUploadStatusChoices.in_progress
        reason = "Scorm Upload is in progress"
        self.logger.info(f"Got ScormUpload Task For : {scorm_instance.name} on {get_current_db_name()}")
        try:
            folder_name = os.path.splitext(file_name)[0]
            local_extraction_path = f"apps/media/temp/{db_name}/scorm/{folder_name}"
            os.makedirs(local_extraction_path, exist_ok=True)
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(local_extraction_path)
            ims_manifest_file_path = f"{local_extraction_path}/imsmanifest.xml"
            if os.path.exists(ims_manifest_file_path):
                base_upload_dir = f"files/{db_name}/scorm"
                upload_dir = os.path.join(base_upload_dir, file_name)
                scorm_file = open(file_path, "rb")
                uploaded_file = default_storage.save(upload_dir, scorm_file)

                # open the uploaded zip file in the default storage
                zip_data = default_storage.open(upload_dir).read()
                extraction_path = f"{base_upload_dir}/{folder_name}"
                with zipfile.ZipFile(BytesIO(zip_data)) as zip_file:
                    blobs_list = zip_file.namelist()
                    self._extract_and_save_files(zip_file, extraction_path)
                scorm_instance.file_url = default_storage.url(f"{extraction_path}")
                try:
                    ims_manifest_file = default_storage.open(f"{extraction_path}/imsmanifest.xml", mode="rb")
                    root = ET.fromstring(ims_manifest_file.read().decode("utf-8"))
                    target_resource = None
                    namespaces = (
                        DEFAULT_SCORM_STANDARD_VERSION_NS
                        if scorm_instance.is_standard
                        else DEFAULT_SCORM_OTHER_VERSION_NS
                    )
                    for resource in root.findall('.//imscp:resource[@adlcp:scormtype="sco"]', namespaces):
                        target_resource = resource
                        break
                    if target_resource and target_resource.attrib.get("href"):
                        launcher_file = target_resource.attrib["href"]
                        scorm_instance.launcher_url = default_storage.url(f"{extraction_path}/{launcher_file}")
                        upload_status = BaseUploadStatusChoices.completed
                        reason = "Scorm uploaded successfully"
                    else:
                        upload_status = BaseUploadStatusChoices.failed
                        reason = "Launcher file not found in target resource"
                except Exception as e:
                    self.logger.error(f"Error: {e}")
                    upload_status = BaseUploadStatusChoices.failed
                    reason = "imsmanifest.xml file not found in the uploaded zip file"
            else:
                reason = "Invalid scorm file"
                upload_status = BaseUploadStatusChoices.failed
                self.logger.error(f"Error: {reason}")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            upload_status = BaseUploadStatusChoices.failed
            reason = "Scorm upload failed"
        finally:
            try:
                os.remove(file_path)
                shutil.rmtree(local_extraction_path)
                path = uploaded_file.split(".")[0]
                default_storage.delete(uploaded_file)
                if upload_status == BaseUploadStatusChoices.failed:
                    for blob in blobs_list:
                        default_storage.delete(f"{path}/{blob}")
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
        scorm_instance.upload_status = upload_status
        scorm_instance.reason = reason
        scorm_instance.save()
        return True

    def _extract_and_save_files(self, zip_file, extraction_path):
        """Function to extract and save the files from a zip file."""

        for extracted_file in zip_file.namelist():
            try:
                if zipfile.Path(zip_file, at=extracted_file).is_file():
                    extracted_file_data = zip_file.read(extracted_file)
                    extracted_blob_name = f"{extraction_path}/{extracted_file}"
                    default_storage.save(extracted_blob_name, BytesIO(extracted_file_data))
            except Exception as e:
                self.logger.error(e)
