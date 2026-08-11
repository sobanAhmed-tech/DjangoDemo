from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="commenter1", password="StrongPassword123")
        self.other_user = User.objects.create_user(username="commenter2", password="StrongPassword123")
        self.post = self.user.posts.create(title="Post for comments", content="Comment here")
        self.client.force_authenticate(user=self.user)

    def test_anonymous_user_can_list_comments(self):
        self.post.comments.create(author=self.user, text="hello world")
        self.client.logout()

        response = self.client.get(reverse("comment-list-create", args=[self.post.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_anonymous_user_cannot_create_comment(self):
        self.client.logout()
        response = self.client.post(reverse("comment-list-create", args=[self.post.id]), {"text": "Nope"}, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_user_can_create_comment(self):
        response = self.client.post(reverse("comment-list-create", args=[self.post.id]), {"text": "Nice post"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user.id)
        self.assertEqual(response.data["post"], self.post.id)

    def test_user_cannot_spoof_comment_author(self):
        response = self.client.post(
            reverse("comment-list-create", args=[self.post.id]),
            {"text": "spoof", "author": self.other_user.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user.id)

    def test_comment_author_can_delete_own_comment(self):
        comment = self.post.comments.create(author=self.user, text="delete me")
        response = self.client.delete(reverse("comment-detail", args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_different_user_cannot_delete_other_comment(self):
        comment = self.post.comments.create(author=self.user, text="not yours")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(reverse("comment-detail", args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comments_are_associated_with_requested_post(self):
        other_post = self.user.posts.create(title="Another Post", content="Second post")
        self.post.comments.create(author=self.user, text="first post comment")
        other_post.comments.create(author=self.user, text="second post comment")

        response = self.client.get(reverse("comment-list-create", args=[self.post.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["post"], self.post.id)
