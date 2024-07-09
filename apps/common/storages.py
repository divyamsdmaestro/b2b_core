from storages.backends.azure_storage import AzureStorage


class StaticRootAzureStorage(AzureStorage):
    location = "static"
    file_overwrite = False


class MediaRootAzureStorage(AzureStorage):
    location = "media"
    file_overwrite = False
