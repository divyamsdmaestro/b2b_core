from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    CreationModel,
    ImageOnlyModel,
    NameModel,
)
from apps.forum.config import ForumTypeChoices, PostTypeChoices
from apps.forum.models.base import ForumBaseModel, PostBaseModel


class ForumImageModel(ImageOnlyModel):
    """
    Image model for Forum.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class Forum(ForumBaseModel):
    """
    Forum model for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, modified_by, deleted_by, forum_image
        Fields      - uuid, description, hashtags, topics
        Unique      - name
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_active, is_deleted
        m2m         - members
        choice      - forum_type

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(ForumBaseModel.Meta):
        default_related_name = "related_forums"

    # Foreign key
    forum_image = models.ForeignKey(
        to=ForumImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Choices
    forum_type = models.CharField(
        choices=ForumTypeChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, default=ForumTypeChoices.private
    )

    # ManyToMany fields
    members = models.ManyToManyField(to="access.User", blank=True)
    hashtag = models.ManyToManyField(to="meta.Hashtag", blank=True)

    @property
    def hashtag_as_name(self):
        """Returns the hashtag names."""

        return self.hashtag.values_list("name", flat=True)


class ForumTopic(NameModel):
    """
    Topic model for IIHT-B2B.

    ********************* Model Fields *********************
    PK          - id
    Unique      - uuid, ss_id
    Fields      - name
    Datetime    - created_at, modified_at

    """

    class Meta(NameModel.Meta):
        default_related_name = "related_forum_topics"

    forum = models.ForeignKey("forum.Forum", on_delete=models.CASCADE)


class PostImageModel(ImageOnlyModel):
    """
    Image model for Forum-Post.

    Model Fields -
        PK          - id,
        FK          - created_by,
        Fields      - uuid, image
        Datetime    - created_at, modified_at

    """

    pass


class Post(PostBaseModel):
    """
    Post model for Forum.

    ********************* Model Fields *********************

        PK          - id,
        Fk          - created_by, forum, post_image
        Fields      - uuid, description, name, hashtags
        Datetime    - created_at, modified_at
        m2m         - poll_options
        URLField    - post_attachment
        DateField   - start_date, end_date
        Bool        - enable_end_time, enable_hide_discussion
        Choice      - post_type

    App QuerySet Manager Methods -
        get_or_none, active, inactive, alive, dead, delete, hard_delete

    """

    class Meta(ForumBaseModel.Meta):
        default_related_name = "related_posts"

    # ForeignKeys
    forum_topic = models.ForeignKey(
        "forum.ForumTopic", on_delete=models.CASCADE, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    post_image = models.ForeignKey(
        to=PostImageModel, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Choices
    post_type = models.CharField(choices=PostTypeChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    # TextFields
    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # ManyToManyFields
    hashtag = models.ManyToManyField(to="meta.Hashtag", blank=True)
    poll_options = models.ManyToManyField(to="forum.PostPollOption", blank=True)

    # URLFields
    post_attachment = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # DateFields
    start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    end_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # BooleanFields
    enable_end_time = models.BooleanField(default=False)
    enable_hide_discussion = models.BooleanField(default=False)

    @property
    def hashtag_as_name(self):
        """Returns the hashtag names."""

        return self.hashtag.values_list("name", flat=True)


class PostLike(CreationModel):
    """
    Like model for Forum Posts.

    ********************* Model Fields *********************
    PK - id
    FK - created_by, post
    Unique - uuid
    Datetime - created_at, modified_at
    Bool  - is_liked
    """

    class Meta(CreationModel.Meta):
        default_related_name = "related_likes"

    # ForeignKeys
    post = models.ForeignKey("forum.Post", on_delete=models.CASCADE)

    # BooleanFields
    is_liked = models.BooleanField(default=False)


class PostPollOption(PostBaseModel):
    """
    PostPollOption model for Forum Posts.

    ********************* Model Fields *********************
    PK - id
    FK - created_by
    Unique - uuid
    fields - clicked_count, name
    Datetime - created_at, modified_at
    """

    class Meta(CreationModel.Meta):
        default_related_name = "related_poll_options"

    clicked_count = models.IntegerField(default=0)


class PostPollOptionClick(CreationModel):
    """
    Poll option clicked model for Forum Posts.

    ********************* Model Fields *********************
    PK - id
    FK - created_by, post, poll_option
    Unique - uuid
    Datetime - created_at, modified_at
    Bool  - is_liked
    """

    class Meta(CreationModel.Meta):
        default_related_name = "related_poll_options_clicked"

    # ForeignKeys
    post = models.ForeignKey("forum.Post", on_delete=models.CASCADE)
    poll_option = models.ForeignKey("forum.PostPollOption", on_delete=models.CASCADE)


class PostComment(PostBaseModel):
    """
    Comment model for Forum Posts.

    ********************* Model Fields *********************
    PK - id
    FK - created_by, post
    Unique - uuid
    fields - name
    Datetime - created_at, modified_at
    """

    class Meta(PostBaseModel.Meta):
        default_related_name = "related_comments"

    post = models.ForeignKey("forum.Post", on_delete=models.CASCADE)


class PostReply(PostBaseModel):
    """
    Reply model for Forum Posts.

    ********************* Model Fields *********************
    PK - id
    FK - created_by, comment
    Unique - uuid
    fields - name
    Datetime - created_at, modified_at
    """

    class Meta(PostBaseModel.Meta):
        default_related_name = "related_replies"

    comment = models.ForeignKey("forum.PostComment", on_delete=models.CASCADE)
