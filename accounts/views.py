from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.pagination import StandardPageNumberPagination

from .models import Follow, Notification
from .serializers import NotificationSerializer, ProfileMeSerializer, UserSummarySerializer
from .utils import are_friends, friend_ids, get_profile


class UserListView(generics.ListAPIView):
    """List/search users (excluding the current user)."""

    serializer_class = UserSummarySerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.exclude(pk=self.request.user.pk)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(username__icontains=search)
        return qs


class SuggestedUsersView(generics.ListAPIView):
    """Users the current user does not follow yet, ranked by how many of
    their followings also follow the candidate (friends-of-friends)."""

    serializer_class = UserSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # small fixed list

    def get_queryset(self):
        me = self.request.user
        my_following = list(
            Follow.objects.filter(follower=me).values_list("following_id", flat=True)
        )
        qs = (
            User.objects.exclude(pk=me.pk)
            .exclude(pk__in=my_following)
            .annotate(
                mutual_count=Count("followers", filter=Q(followers__follower_id__in=my_following))
            )
            .order_by("-mutual_count", "id")[:10]
        )
        return qs


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_url_kwarg = "user_id"


class ProfileMeView(generics.RetrieveUpdateAPIView):
    """View (GET) / update (PATCH) the current user's profile + privacy settings."""

    serializer_class = ProfileMeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return get_profile(self.request.user)


class FollowView(APIView):
    """Follow (POST) / unfollow (DELETE) a user."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=400)
        _, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if created:
            Notification.objects.create(
                recipient=target, actor=request.user, verb=Notification.FOLLOW
            )
        return Response(
            {"following": True, "is_friend": are_friends(request.user, target)}
        )

    def delete(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        Follow.objects.filter(follower=request.user, following=target).delete()
        return Response(
            {"following": False, "is_friend": are_friends(request.user, target)}
        )


class FollowersView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_id"])
        follower_ids = Follow.objects.filter(following=user).values_list("follower_id", flat=True)
        return User.objects.filter(pk__in=list(follower_ids))


class FollowingView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_id"])
        following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        return User.objects.filter(pk__in=list(following_ids))


class MutualFriendsView(generics.ListAPIView):
    """Users who are mutual friends ("friends") with BOTH the current user
    and the target user."""

    serializer_class = UserSummarySerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        me = self.request.user
        target = get_object_or_404(User, pk=self.kwargs["user_id"])
        mutual_ids = friend_ids(me) & friend_ids(target)
        return User.objects.filter(pk__in=list(mutual_ids))


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = StandardPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related(
            "actor", "post"
        )


class NotificationReadView(APIView):
    """Mark all of the current user's notifications as read."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return Response({"marked_read": updated})
