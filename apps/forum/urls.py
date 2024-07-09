from django.urls import path

from apps.common.routers import AppSimpleRouter

from .views.api.v1 import (
    ForumCUDApiViewSet,
    ForumImageUploadAPIView,
    ForumListApiViewSet,
    ForumRetrieveApiViewSet,
    ForumTopicListApiViewSet,
    PostCommentCUDApiViewSet,
    PostCommentListApiViewSet,
    PostCUDApiViewSet,
    PostImageUploadAPIView,
    PostLikeApiView,
    PostListApiViewSet,
    PostPollOptionClickApiView,
    PostReplyCUDApiViewSet,
    PostReplyListApiViewSet,
)

app_name = "forum"
API_URL_PREFIX = "api/v1/forum"

router = AppSimpleRouter()

# Forum Api's
router.register(f"{API_URL_PREFIX}/cud", ForumCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/detail", ForumRetrieveApiViewSet)
router.register(f"{API_URL_PREFIX}/list", ForumListApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<forum_id>[^/.]+)/topic/list", ForumTopicListApiViewSet)
# Forum Post Api's
router.register(f"{API_URL_PREFIX}/post/cud", PostCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/(?P<topic_id>[^/.]+)/post/list", PostListApiViewSet)
# Forum Post Comment Api's
router.register(f"{API_URL_PREFIX}/post/comment/cud", PostCommentCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/post/(?P<post_id>[^/.]+)/comment/list", PostCommentListApiViewSet)
# Forum Post Reply Api's
router.register(f"{API_URL_PREFIX}/post/comment/reply/cud", PostReplyCUDApiViewSet)
router.register(
    f"{API_URL_PREFIX}/post/comment/(?P<comment_id>[^/.]+)/reply/list",
    PostReplyListApiViewSet,
)

urlpatterns = [
    path(f"{API_URL_PREFIX}/image/upload/", ForumImageUploadAPIView.as_view(), name="forum-image-upload"),
    path(f"{API_URL_PREFIX}/post/image/upload/", PostImageUploadAPIView.as_view(), name="post-image-upload"),
    path(f"{API_URL_PREFIX}/post/<post_id>/like/", PostLikeApiView.as_view()),
    path(
        f"{API_URL_PREFIX}/post/polloption/<poll_option_id>/",
        PostPollOptionClickApiView.as_view(),
    ),
] + router.urls
