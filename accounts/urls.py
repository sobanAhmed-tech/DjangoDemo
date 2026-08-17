from django.urls import path

from .views import (
    FollowersView,
    FollowingView,
    FollowView,
    MutualFriendsView,
    NotificationListView,
    NotificationReadView,
    ProfileMeView,
    SuggestedUsersView,
    UserDetailView,
    UserListView,
    FollowRequestListView,
    FollowRequestActionView,
)

urlpatterns = [
    # Current user's own profile + privacy settings
    path("profile/me/", ProfileMeView.as_view(), name="profile-me"),
    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/read/", NotificationReadView.as_view(), name="notification-read"),
    # User discovery
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/suggested/", SuggestedUsersView.as_view(), name="user-suggested"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
    # Follow graph
    path("users/<int:user_id>/follow/", FollowView.as_view(), name="user-follow"),
    path("users/<int:user_id>/followers/", FollowersView.as_view(), name="user-followers"),
    path("users/<int:user_id>/following/", FollowingView.as_view(), name="user-following"),
    path("users/<int:user_id>/mutual-friends/", MutualFriendsView.as_view(), name="user-mutual-friends"),
    path("follow-requests/", FollowRequestListView.as_view(), name="follow-requests-list"),
    path("follow-requests/<int:requester_id>/", FollowRequestActionView.as_view(), name="follow-requests-action"),
]
