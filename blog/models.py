from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", related_name="comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Like(models.Model):
    """A user's like on a post. One like per user per post."""

    user = models.ForeignKey(User, related_name="likes", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_like"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes '{self.post.title}'"


class SavedPost(models.Model):
    """A user's bookmarked (saved) post for later viewing."""

    user = models.ForeignKey(User, related_name="saved_posts", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", related_name="saved_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_saved_post"),
        ]
        ordering = ["-created_at"]
        verbose_name = "Saved post"
        verbose_name_plural = "Saved posts"

    def __str__(self):
        return f"{self.user.username} saved '{self.post.title}'"
