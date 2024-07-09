from datetime import date

from django.db.models import Q
from rest_framework.generics import get_object_or_404

from apps.common.views.api import (
    AppAPIView,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
    get_upload_api_view,
)
from apps.forum.models import (
    Forum,
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
from apps.forum.serializers.v1 import (
    ForumCUDModelSerializer,
    ForumDetailSerializer,
    ForumListSerializer,
    ForumTopicListSerializer,
    PostCommentCUDModelSerializer,
    PostCommentDetailSerializer,
    PostCUDModelSerializer,
    PostDetailSerializer,
    PostReplyCUDModelSerializer,
    PostReplyDetailSerializer,
)

ForumImageUploadAPIView = get_upload_api_view(meta_model=ForumImageModel, meta_fields=["id", "image"])

PostImageUploadAPIView = get_upload_api_view(meta_model=PostImageModel, meta_fields=["id", "image"])


class ForumCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete forums."""

    serializer_class = ForumCUDModelSerializer
    queryset = Forum.objects.alive()


class ForumRetrieveApiViewSet(AppModelRetrieveAPIViewSet):
    """Viewset to retrieve the particular forum details."""

    serializer_class = ForumDetailSerializer
    queryset = Forum.objects.alive()


class ForumListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list forums."""

    queryset = Forum.objects.alive().order_by("created_at")
    search_fields = ["name"]
    filterset_fields = [
        "related_forum_course_relations__course",
        "related_learning_paths",
        "related_advanced_learning_paths",
        "related_skill_travellers",
        "related_playgrounds",
        "related_playground_groups",
    ]
    serializer_class = ForumListSerializer


class ForumTopicListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list forum topics."""

    serializer_class = ForumTopicListSerializer

    def get_queryset(self, *args, **kwargs):
        """Overridden to filter the queryset based on forums"""

        forum = get_object_or_404(Forum, id=self.kwargs.get("forum_id", None))

        return ForumTopic.objects.filter(forum=forum).order_by("created_at")


class PostCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete posts."""

    serializer_class = PostCUDModelSerializer
    queryset = Post.objects.all()


class PostListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list posts."""

    search_fields = ["name"]
    serializer_class = PostDetailSerializer

    def get_queryset(self, *args, **kwargs):
        """Overridden the queryset to filter the posts based on forum topics."""

        topic = get_object_or_404(ForumTopic, id=self.kwargs.get("topic_id", None))

        return (
            Post.objects.filter(forum_topic=topic)
            .filter(Q(enable_end_time=False) | Q(enable_end_time=True, end_date__gt=date.today()))
            .order_by("created_at")
        )


class PostCommentCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete comments."""

    serializer_class = PostCommentCUDModelSerializer
    queryset = PostComment.objects.all()


class PostCommentListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list comments."""

    serializer_class = PostCommentDetailSerializer

    def get_queryset(self, *args, **kwargs):
        """Overriden to filter comments based on the post"""

        post = get_object_or_404(Post, id=self.kwargs.get("post_id", None))

        return PostComment.objects.filter(post=post).order_by("created_at")


class PostReplyCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete replies."""

    serializer_class = PostReplyCUDModelSerializer
    queryset = PostReply.objects.all()


class PostReplyListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list replies."""

    serializer_class = PostReplyDetailSerializer

    def get_queryset(self, *args, **kwargs):
        """Overriden to filter replies based on the comment"""

        comment = get_object_or_404(PostComment, id=self.kwargs.get("comment_id", None))

        return PostReply.objects.filter(comment=comment).order_by("created_at")


class PostLikeApiView(AppAPIView):
    """View to like the forum post"""

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs.get("post_id", None))
        user = self.get_user()

        post_like, created = PostLike.objects.get_or_create(post=post, created_by=user)
        if created:
            post_like.is_liked = True
        else:
            post_like.is_liked = not post_like.is_liked
        post_like.save()

        return self.send_response()


class PostPollOptionClickApiView(AppAPIView):
    """View to handle the forum poll options in poll based posts"""

    def post(self, request, *args, **kwargs):
        """View to click on the forum poll options"""

        option = get_object_or_404(PostPollOption, id=self.kwargs.get("poll_option_id", None))
        post = option.related_posts.first()

        user = self.get_user()

        # Check if the user already clicked any option before
        existing_click = PostPollOptionClick.objects.filter(post=post, created_by=user).first()

        if existing_click:
            # different option, update the clicked count
            if existing_click.poll_option != option:
                existing_option = existing_click.poll_option
                existing_option.clicked_count = existing_option.related_poll_options_clicked.exclude(
                    created_by=user
                ).count()
                existing_option.save()

                existing_click.poll_option = option
                existing_click.save()

                option.clicked_count = option.related_poll_options_clicked.count()
                option.save()

            else:
                # same option again, decrease the clicked count
                option.clicked_count = option.related_poll_options_clicked.exclude(created_by=user).count()
                option.save()
                existing_click.delete()
        else:
            PostPollOptionClick.objects.create(post=post, poll_option=option, created_by=user)
            # not clicked any option, update the clicked count
            option.clicked_count = option.related_poll_options_clicked.count()
            option.save()

        return self.send_response()
