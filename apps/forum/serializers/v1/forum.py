from rest_framework import serializers

from apps.access.models import User
from apps.access.serializers.v1 import SimpleUserReadOnlyModelSerializer
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.forum.config import ForumTypeChoices, PostTypeChoices
from apps.forum.models import (
    Forum,
    ForumCourseRelationModel,
    ForumImageModel,
    ForumTopic,
    Post,
    PostComment,
    PostImageModel,
    PostLike,
    PostPollOption,
    PostPollOptionClick,
    PostReply,
)
from apps.forum.serializers.v1.base import CommonForumCUDModelSerializer, CommonForumDetailSerializer
from apps.leaderboard.config import MilestoneChoices
from apps.leaderboard.tasks import CommonLeaderboardTask
from apps.learning.models import Course
from apps.tenant_service.middlewares import get_current_db_name


class ForumCUDModelSerializer(CommonForumCUDModelSerializer):
    """Forum model serializer holds create, update & destroy."""

    courses = serializers.PrimaryKeyRelatedField(queryset=Course.objects.alive(), many=True, required=False)
    forum_topic = serializers.ListField(
        child=serializers.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, required=False)
    )

    class Meta(CommonForumCUDModelSerializer.Meta):
        model = Forum
        fields = [
            "name",
            "description",
            "hashtag",
            "forum_topic",
            "forum_type",
            "forum_image",
            "members",
            "courses",
        ]

    def create(self, validated_data):
        """Overridden to add courses to forum."""

        courses = validated_data.pop("courses")
        forum_topics = validated_data.pop("forum_topic")
        instance = super().create(validated_data=validated_data)
        if courses:
            ForumCourseRelationModel.objects.bulk_create(
                ForumCourseRelationModel(forum=instance, course=course) for course in courses
            )
        if forum_topics:
            ForumTopic.objects.bulk_create(ForumTopic(forum=instance, name=topic) for topic in forum_topics)
        return instance

    def update(self, instance, validated_data):
        """Overridden to update the courses in forum."""

        courses = validated_data.pop("courses")
        forum_topics = validated_data.pop("forum_topic")
        instance = super().update(instance=instance, validated_data=validated_data)
        if courses:
            instance.related_forum_course_relations.exclude(course__in=courses).delete()
            for course in courses:
                ForumCourseRelationModel.objects.update_or_create(forum=instance, course=course)
        else:
            instance.related_forum_course_relations.all().delete()
        if forum_topics:
            instance.related_forum_topics.exclude(name__in=forum_topics).delete()
            for topic in forum_topics:
                ForumTopic.objects.update_or_create(forum=instance, name=topic)
        else:
            instance.related_forum_topics.all().delete()
        return instance

    def get_meta_initial(self):
        """Returns the initial data."""

        meta = super().get_meta_initial()
        meta["courses"] = Course.objects.filter(related_forum_course_relations__forum=self.instance).values_list(
            "id", flat=True
        )
        meta["forum_topic"] = ForumTopic.objects.filter(forum=self.instance).values_list("name", flat=True)
        return meta

    def get_meta(self) -> dict:
        """Get meta & initial values for forums."""

        return {
            "members": self.serialize_for_meta(User.objects.alive(), fields=["id", "username"]),
            "courses": self.serialize_for_meta(Course.objects.alive(), fields=["id", "name"]),
            "forum_type": self.serialize_dj_choices(ForumTypeChoices.choices),
        }


class ForumDetailSerializer(CommonForumDetailSerializer):
    """Retrieve serializer for forum."""

    forum_image = read_serializer(ForumImageModel, meta_fields=["id", "uuid", "image"])(ForumImageModel.objects.all())
    members = read_serializer(meta_model=User, meta_fields=["id", "uuid", "first_name"])(
        User.objects.alive(), many=True
    )
    courses = serializers.SerializerMethodField()

    def get_courses(self, obj):
        """Return a list of courses related to the forum."""

        courses = Course.objects.filter(related_forum_course_relations__forum=obj).alive().order_by("created_at")
        return read_serializer(meta_model=Course, meta_fields=["id", "name", "code"])(courses, many=True).data

    class Meta:
        model = Forum
        fields = [
            "id",
            "name",
            "description",
            "hashtag",
            "forum_type",
            "forum_image",
            "members",
            "courses",
        ]


class ForumListSerializer(AppReadOnlyModelSerializer):
    """Retrieve serializer for forum listing."""

    forum_image = read_serializer(ForumImageModel, meta_fields=["id", "uuid", "image"])(ForumImageModel.objects.all())
    members_count = serializers.SerializerMethodField()
    topic_count = serializers.SerializerMethodField()
    no_of_posts = serializers.SerializerMethodField()

    class Meta:
        model = Forum
        fields = [
            "id",
            "name",
            "description",
            "forum_image",
            "created_at",
            "forum_type",
            "members_count",
            "topic_count",
            "no_of_posts",
        ]

    def get_topic_count(self, obj):
        """Returns the topic count of the forum."""

        return obj.related_forum_topics.count()

    def get_members_count(self, obj):
        """Returns the members count of the forum."""

        return obj.members.count()

    def get_no_of_posts(self, obj):
        """Returns the posts count of the forum."""

        return Post.objects.filter(forum_topic__forum=obj).count()


class ForumTopicListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for the forum topic list."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = ForumTopic
        fields = [
            "id",
            "name",
            "forum",
        ]


class PollOptionsHandleSerializer(AppWriteOnlyModelSerializer):
    """Handle serialization of a PollOptions"""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PostPollOption
        fields = ["name"]


class PostCUDModelSerializer(CommonForumCUDModelSerializer):
    """Post model serializer holds create, update & destroy."""

    poll_options = PollOptionsHandleSerializer(many=True)

    class Meta(CommonForumCUDModelSerializer.Meta):
        model = Post
        fields = [
            "name",
            "description",
            "forum_topic",
            "post_image",
            "post_type",
            "hashtag",
            "poll_options",
            "post_attachment",
            "start_date",
            "end_date",
            "enable_end_time",
            "enable_hide_discussion",
        ]

    def create(self, validated_data):
        """overriden to create poll options"""

        poll_options = validated_data.pop("poll_options", [])
        instance = super().create(validated_data)
        for poll_option in poll_options:
            instance.poll_options.create(**poll_option)
        CommonLeaderboardTask().run_task(
            milestone_names=MilestoneChoices.forum_post_creation,
            user_id=self.get_user().id,
            db_name=get_current_db_name(),
            forum_id=instance.forum_topic.forum_id,
        )
        return instance

    def update(self, instance, validated_data):
        """overriden to update poll options"""

        poll_options_data = validated_data.pop("poll_options", [])
        instance = super().update(instance, validated_data)
        # M2M fields
        if poll_options_data:
            instance.poll_options.clear()
            for data in poll_options_data:
                poll_options = PostPollOption.objects.filter(**data)
                if poll_options.exists():
                    poll_option = poll_options.first()
                else:
                    poll_option = PostPollOption.objects.create(**data)
                instance.poll_options.add(poll_option)

        return instance

    def get_meta(self) -> dict:
        """Get meta & initial values for forums."""

        return {
            "post_type": self.serialize_dj_choices(PostTypeChoices.choices),
            "forum_topic": self.serialize_for_meta(ForumTopic.objects.all(), fields=["id", "name", "forum"]),
        }

    def get_meta_initial(self):
        """Overridden to update the allocated poll options details in meta."""

        data = super().get_meta_initial()
        data.update(
            {
                "poll_options": self.serialize_for_meta(
                    queryset=self.instance.poll_options.all(),
                    fields=[
                        "id",
                        "name",
                    ],
                )
            }
        )
        return data


class PostDetailSerializer(CommonForumDetailSerializer):
    """This serializer contains configuration for Post."""

    poll_options = serializers.SerializerMethodField()
    post_image = read_serializer(PostImageModel, meta_fields=["id", "uuid", "image"])(PostImageModel.objects.all())
    created_by = SimpleUserReadOnlyModelSerializer()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_poll_option_clicked = serializers.SerializerMethodField()
    is_my_post = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Post
        fields = [
            "id",
            "uuid",
            "post_type",
            "forum_topic",
            "name",
            "description",
            "hashtag",
            "post_image",
            "poll_options",
            "post_attachment",
            "enable_end_time",
            "start_date",
            "end_date",
            "enable_hide_discussion",
            "likes_count",
            "comments_count",
            "created_by",
            "created_at",
            "modified_at",
            "is_liked",
            "is_poll_option_clicked",
            "is_my_post",
        ]

    def get_poll_options(self, obj):
        """Overriden to return a list of poll options in order of created time."""

        poll_options = obj.poll_options.all()
        return (
            read_serializer(PostPollOption, meta_fields=["id", "uuid", "name", "clicked_count"])(
                poll_options.order_by("created_at"), many=True
            ).data
            if poll_options
            else None
        )

    def get_likes_count(self, obj):
        """Returns the likes count of the posts."""

        return obj.related_likes.filter(is_liked=True).count()

    def get_comments_count(self, obj):
        """Returns the comments count of the posts."""

        return obj.related_comments.count()

    def get_is_liked(self, obj):
        """Returns the post is already liked by a user or not."""

        return PostLike.objects.filter(is_liked=True, created_by=self.get_user(), post=obj).exists()

    def get_is_poll_option_clicked(self, obj):
        """Returns id of poll_option clicked by a user."""

        is_clicked = PostPollOptionClick.objects.filter(created_by=self.get_user(), post=obj).first()
        return is_clicked.poll_option.id if is_clicked else None

    def get_is_my_post(self, obj):
        """Returns the post is created by the current user or not."""

        return obj.created_by == self.get_user()


class PostCommentCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Comment model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PostComment
        fields = [
            "name",
            "post",
        ]

    def create(self, validated_data):
        """Overridden to call leaderboard task"""

        instance = super().create(validated_data)
        CommonLeaderboardTask().run_task(
            milestone_names=MilestoneChoices.forum_post_comments,
            user_id=self.get_user().id,
            db_name=get_current_db_name(),
            forum_id=instance.post.forum_topic.forum_id,
        )
        return instance


class PostCommentDetailSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Post-Comments."""

    replies_count = serializers.SerializerMethodField()
    is_my_comment = serializers.SerializerMethodField()
    created_by = SimpleUserReadOnlyModelSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = ["id", "uuid", "name", "replies_count", "created_by", "created_at", "is_my_comment"]
        model = PostComment

    def get_replies_count(self, obj):
        """Returns the replies count of the posts."""

        return obj.related_replies.count()

    def get_is_my_comment(self, obj):
        """Returns the comment is created by the current user or not."""

        return obj.created_by == self.get_user()


class PostReplyCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Post reply model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PostReply
        fields = [
            "name",
            "comment",
        ]

    def create(self, validated_data):
        """Overridden to call Leaderboard task."""

        instance = super().create(validated_data)
        CommonLeaderboardTask().run_task(
            milestone_names=MilestoneChoices.replying_comments,
            user_id=self.get_user().id,
            db_name=get_current_db_name(),
            forum_id=instance.comment.post.forum_topic.forum_id,
        )
        return instance


class PostReplyDetailSerializer(AppReadOnlyModelSerializer):
    """This serializer contains configuration for Post-replies."""

    created_by = SimpleUserReadOnlyModelSerializer()
    is_my_reply = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = ["id", "uuid", "name", "created_by", "created_at", "is_my_reply"]
        model = PostReply

    def get_is_my_reply(self, obj):
        """Returns the reply is created by the current user or not."""

        return obj.created_by == self.get_user()
