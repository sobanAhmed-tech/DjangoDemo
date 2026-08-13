from django.contrib import admin

from .models import Follow, Notification, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "allow_likes_from", "allow_comments_from", "created_at")
    list_filter = ("allow_likes_from", "allow_comments_from")
    search_fields = ("user__username",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "verb", "read", "created_at")
    list_filter = ("verb", "read")
    search_fields = ("recipient__username", "actor__username")
