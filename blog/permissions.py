from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsAuthorOrReadOnly(BasePermission):
    message = "You can only modify your own post."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:

            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsCommentAuthorOrReadOnly(BasePermission):
    message = "You can only delete your own comment or comments on your post."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or obj.post.author == request.user
