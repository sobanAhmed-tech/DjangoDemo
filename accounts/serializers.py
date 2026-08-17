from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Follow, Notification, Profile, FollowRequest
from .utils import are_friends, get_profile, is_following


class UserSummarySerializer(serializers.ModelSerializer):
    """Public summary of a user with social stats and the requesting
    user's relationship to them."""

    bio = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    has_pending_request = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "bio",
            "post_count",
            "follower_count",
            "following_count",
            "is_following",
            "is_friend",
            "has_pending_request",
        )

    def _me(self):
        request = self.context.get("request")
        return request.user if request and request.user.is_authenticated else None

    def get_bio(self, obj):
        return get_profile(obj).bio

    def get_post_count(self, obj):
        return obj.posts.count()

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        me = self._me()
        return me is not None and is_following(me, obj)

    def get_is_friend(self, obj):
        me = self._me()
        return me is not None and are_friends(me, obj)

    def get_has_pending_request(self, obj):
        me = self._me()
        return me is not None and FollowRequest.objects.filter(requester=me, target=obj).exists()


class ProfileMeSerializer(serializers.ModelSerializer):
    """The current user's own profile, including privacy settings."""

    username = serializers.CharField(source="user.username", read_only=True)
    post_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "username",
            "bio",
            "is_private",
            "allow_likes_from",
            "allow_comments_from",
            "post_count",
            "follower_count",
            "following_count",
        )

    def get_post_count(self, obj):
        return obj.user.posts.count()

    def get_follower_count(self, obj):
        return obj.user.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True, default=None)
    verb_display = serializers.CharField(source="get_verb_display", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "actor_username",
            "verb",
            "verb_display",
            "post",
            "post_title",
            "read",
            "created_at",
        )
        read_only_fields = fields
