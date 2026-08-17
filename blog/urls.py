from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommentDetailView,
    CommentListCreateView,
    FeedView,
    PostLikeView,
    PostSaveView,
    PostViewSet,
    SavedPostsView,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    # Social interactions
    path("feed/", FeedView.as_view(), name="feed"),
    path("posts/saved/", SavedPostsView.as_view(), name="saved-posts"),
    path("posts/<int:post_id>/like/", PostLikeView.as_view(), name="post-like"),
    path("posts/<int:post_id>/save/", PostSaveView.as_view(), name="post-save"),
    # Comments
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("comments/<int:comment_id>/", CommentDetailView.as_view(), name="comment-detail"),
    
    path("", include(router.urls)),
]
