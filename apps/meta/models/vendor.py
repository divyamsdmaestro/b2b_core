from django.db import models

from apps.common.model_fields import AppPhoneNumberField
from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, UniqueNameModel


class Vendor(UniqueNameModel):
    """
    Vendor model for IIHT-B2B.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    Fields      - name, email, contact_number
    Datetime    - created_at, modified_at

    """

    class Meta(UniqueNameModel.Meta):
        default_related_name = "related_vendors"

    email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    contact_number = AppPhoneNumberField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
