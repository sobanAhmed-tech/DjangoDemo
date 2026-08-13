from django.contrib import admin

from .models import Comment, Like, Post, SavedPost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("title", "content", "author__username")
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    list_filter = ("created_at", "author", "post")
    search_fields = ("text", "author__username", "post__title")
    ordering = ("-created_at",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username", "post__title")
    ordering = ("-created_at",)


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username", "post__title")
    ordering = ("-created_at",)
