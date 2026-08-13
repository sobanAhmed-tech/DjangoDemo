from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Follow, Notification
from accounts.utils import can_comment, can_like

from .models import Comment, Like, Post, SavedPost
from .pagination import StandardPageNumberPagination
from .permissions import IsAuthorOrReadOnly, IsCommentAuthorOrReadOnly
from .serializers import CommentSerializer, PostSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["author"]
    search_fields = ["title", "content"]
    pagination_class = StandardPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FeedView(generics.ListAPIView):
    """Home feed: posts from the current user + everyone they follow."""

    serializer_class = PostSerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = list(
            Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        )
        author_ids = following_ids + [user.id]
        return Post.objects.filter(author_id__in=author_ids).select_related("author")


class SavedPostsView(generics.ListAPIView):
    """Posts the current user has bookmarked."""

    serializer_class = PostSerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Post.objects.filter(saved_by__user=self.request.user)
            .select_related("author")
            .order_by("-savedpost__created_at")
        )


class PostLikeView(APIView):
    """Like (POST) / unlike (DELETE) a post, gated by the author's privacy."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if not can_like(request.user, post.author):
            return Response(
                {"detail": "This user does not allow you to like their posts."},
                status=403,
            )
        _, created = Like.objects.get_or_create(user=request.user, post=post)
        if created and post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb=Notification.LIKE,
                post=post,
            )
        return Response({"liked": True, "like_count": post.likes.count()})

    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({"liked": False, "like_count": post.likes.count()})


class PostSaveView(APIView):
    """Save (POST) / unsave (DELETE) a bookmark."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        SavedPost.objects.get_or_create(user=request.user, post=post)
        return Response({"saved": True})

    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        SavedPost.objects.filter(user=request.user, post=post).delete()
        return Response({"saved": False})


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return Comment.objects.filter(post=post).select_related("author", "post", "post__author")

    def create(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if not can_comment(request.user, post.author):
            return Response(
                {"detail": "This user does not allow you to comment on their posts."},
                status=403,
            )
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"text": ["Text cannot be blank."]}, status=400)
        comment = Comment.objects.create(post=post, author=request.user, text=text)
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb=Notification.COMMENT,
                post=post,
            )
        return Response(CommentSerializer(comment, context={"request": request}).data, status=201)


class CommentDetailView(generics.DestroyAPIView):
    """Delete a comment. Allowed for the comment author OR the post owner
    (Instagram-style: post owners can moderate comments on their posts)."""

    queryset = Comment.objects.select_related("author", "post", "post__author")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]
    lookup_url_kwarg = "comment_id"
    lookup_field = "id"
