from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    CreationAndModificationModel,
)


class TenantAddress(CreationAndModificationModel):
    """
    TenantAddress model for IIHT-B2B. Requirement came while integrating KeyCloak Integrations 27-12-23.

    Model Fields -
        PK          - id,
        Fk          - created_by, modified_by, tenant, country, state, city
        Fields      - uuid, ss_id, address_line_one, address_line_two, pincode
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(CreationAndModificationModel.Meta):
        default_related_name = "related_tenant_addresses"

    # FKs
    tenant = models.ForeignKey("tenant.Tenant", on_delete=models.CASCADE)
    country = models.ForeignKey("meta.Country", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    state = models.ForeignKey("meta.State", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    city = models.ForeignKey("meta.City", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # Fields
    address_line_one = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    address_line_two = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    pincode = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def __str__(self):
        """Address line 1 as string representation."""

        return self.address_line_one
