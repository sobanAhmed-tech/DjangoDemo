from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra user information: bio + privacy settings for who can
    like / comment on that user's posts."""

    PRIVACY_EVERYONE = "everyone"
    PRIVACY_FRIENDS = "friends"
    PRIVACY_NOBODY = "nobody"
    PRIVACY_CHOICES = [
        (PRIVACY_EVERYONE, "Everyone"),
        (PRIVACY_FRIENDS, "Friends only (mutual follows)"),
        (PRIVACY_NOBODY, "Nobody"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    bio = models.TextField(blank=True, default="")
    is_private = models.BooleanField(default=False)
    allow_likes_from = models.CharField(
        max_length=10, choices=PRIVACY_CHOICES, default=PRIVACY_EVERYONE
    )
    allow_comments_from = models.CharField(
        max_length=10, choices=PRIVACY_CHOICES, default=PRIVACY_EVERYONE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username}'s profile"


class Follow(models.Model):
    """Directional follow relationship.
    A "friend" / "mutual friend" is two users who follow each other."""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


class FollowRequest(models.Model):
    """Pending request to follow a private profile."""

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_follow_requests", on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="received_follow_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["requester", "target"], name="unique_follow_request"
            ),
            models.CheckConstraint(
                check=~models.Q(requester=models.F("target")),
                name="prevent_self_follow_request",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.requester.username} requests to follow {self.target.username}"


class Notification(models.Model):
    """Activity notifications: who did what (optionally on which post)."""

    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    FOLLOW_REQUEST = "follow_request"
    FOLLOW_ACCEPT = "follow_accept"
    VERB_CHOICES = [
        (LIKE, "liked your post"),
        (COMMENT, "commented on your post"),
        (FOLLOW, "started following you"),
        (FOLLOW_REQUEST, "requested to follow you"),
        (FOLLOW_ACCEPT, "accepted your follow request"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="actions",
        on_delete=models.CASCADE,
    )
    verb = models.CharField(max_length=20, choices=VERB_CHOICES)
    post = models.ForeignKey(
        "blog.Post", related_name="notifications", on_delete=models.CASCADE, null=True, blank=True
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "-created_at"])]

    def __str__(self):
        target = f" on '{self.post.title}'" if self.post else ""
        return f"{self.actor.username} {self.get_verb_display()}{target} → {self.recipient.username}"
