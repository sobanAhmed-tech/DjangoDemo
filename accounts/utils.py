"""Shared helpers for follow relationships and privacy checks."""
from django.contrib.auth.models import User

from .models import Follow, Profile


def are_friends(user_a: User, user_b: User) -> bool:
    """True if user_a and user_b follow each other (mutual follow = 'friends')."""
    if user_a is None or user_b is None or user_a == user_b:
        # A user is always considered able to act on their own content.
        return user_a == user_b
    return Follow.objects.filter(
        follower=user_a, following=user_b
    ).exists() and Follow.objects.filter(follower=user_b, following=user_a).exists()


def is_following(follower: User, target: User) -> bool:
    """True if `follower` follows `target` (one-directional)."""
    if follower is None or target is None:
        return False
    return Follow.objects.filter(follower=follower, following=target).exists()


def friend_ids(user: User) -> set:
    """Return the set of user IDs who are mutual follows ("friends") with `user`."""
    if user is None:
        return set()
    following = set(
        Follow.objects.filter(follower=user).values_list("following_id", flat=True)
    )
    followers = set(
        Follow.objects.filter(following=user).values_list("follower_id", flat=True)
    )
    return following & followers


def get_profile(user: User) -> Profile:
    """Return a user's profile, creating it if missing (legacy users)."""
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def can_like(actor: User, post_author: User) -> bool:
    """Whether `actor` is allowed to like `post_author`'s posts,
    based on the author's allow_likes_from privacy setting."""
    if actor == post_author:
        return True
    setting = get_profile(post_author).allow_likes_from
    if setting == Profile.PRIVACY_EVERYONE:
        return True
    if setting == Profile.PRIVACY_FRIENDS:
        return are_friends(actor, post_author)
    return False  # PRIVACY_NOBODY


def can_comment(actor: User, post_author: User) -> bool:
    """Whether `actor` is allowed to comment on `post_author`'s posts."""
    if actor == post_author:
        return True
    setting = get_profile(post_author).allow_comments_from
    if setting == Profile.PRIVACY_EVERYONE:
        return True
    if setting == Profile.PRIVACY_FRIENDS:
        return are_friends(actor, post_author)
    return False  # PRIVACY_NOBODY
