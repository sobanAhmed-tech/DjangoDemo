from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.utils import can_comment, can_like, get_profile, is_following

from .models import Comment, Post


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "password", "password2")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Enriched post payload with social context: author details, counts,
    and the requesting user's relationship to the post (liked/saved/following)."""

    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.SerializerMethodField()
    author_bio = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_following_author = serializers.SerializerMethodField()
    can_like = serializers.SerializerMethodField()
    can_comment = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "author_bio",
            "created_at",
            "like_count",
            "comment_count",
            "is_liked",
            "is_saved",
            "is_following_author",
            "can_like",
            "can_comment",
        )
        read_only_fields = ("id", "author", "created_at")

    # --- helpers ---
    def _user(self):
        request = self.context.get("request")
        return request.user if request and request.user.is_authenticated else None

    # --- fields ---
    def get_author_username(self, obj):
        return obj.author.username

    def get_author_bio(self, obj):
        return get_profile(obj.author).bio

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        user = self._user()
        return user is not None and obj.likes.filter(user=user).exists()

    def get_is_saved(self, obj):
        user = self._user()
        return user is not None and obj.saved_by.filter(user=user).exists()

    def get_is_following_author(self, obj):
        user = self._user()
        return user is not None and is_following(user, obj.author)

    def get_can_like(self, obj):
        user = self._user()
        return user is not None and can_like(user, obj.author)

    def get_can_comment(self, obj):
        user = self._user()
        return user is not None and can_comment(user, obj.author)

    # --- validation ---
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be blank.")
        return value.strip()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "author_username", "post", "created_at")
        read_only_fields = ("id", "author", "post", "created_at")

    def get_author_username(self, obj):
        return obj.author.username

    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Text cannot be blank.")
        return value.strip()
