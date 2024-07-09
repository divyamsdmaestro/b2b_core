from apps.common.models import UniqueNameModel


class Hashtag(UniqueNameModel):
    """
    Hashtag model for IIHT-B2B.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    Fields      - name
    Datetime    - created_at, modified_at

    """

    class Meta(UniqueNameModel.Meta):
        default_related_name = "related_hashtags"

    pass
