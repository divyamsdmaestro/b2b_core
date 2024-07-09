from django.db import models

from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
from apps.my_learning.models import BaseUserTrackingModel


class UserPlaygroundGroupTracker(BaseUserTrackingModel):
    """
    User Playground Group Tracking Model for IIHT-B2B.
    Model Fields -
        PK          - id,
        Fk          - created_by, playground_group, enrolled_to
        Fields      - uuid, ss_id, actionee, action, reason
        Numeric     - progress
        Datetime    - valid_till, last_accessed_on, created_at, modified_at, action_date
        Bool        - is_started, is_completed,is_tenant_admin_approval, is_super_admin_approval, is_self_enrolled,

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(BaseUserTrackingModel.Meta):
        default_related_name = "related_user_playground_group_trackers"

    playground_group = models.ForeignKey(
        to="learning.PlaygroundGroup", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
