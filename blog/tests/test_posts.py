from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PostAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author1", password="StrongPassword123")
        self.other_user = User.objects.create_user(username="author2", password="StrongPassword123")
        self.client.force_authenticate(user=self.user)

    def test_anonymous_user_can_list_posts(self):
        self.client.logout()
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_post(self):
        self.client.logout()
        response = self.client.post(reverse("post-list"), {"title": "No access", "content": "Should fail"}, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_user_can_create_post(self):
        response = self.client.post(reverse("post-list"), {"title": "Hello Django", "content": "This is my first post."}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user.id)

    def test_user_cannot_spoof_author(self):
        response = self.client.post(
            reverse("post-list"),
            {"title": "Spoof", "content": "Should not assign other user", "author": self.other_user.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user.id)

    def test_user_can_retrieve_post(self):
        post = self.user.posts.create(title="Retrieve Me", content="Content here")
        response = self.client.get(reverse("post-detail", args=[post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Retrieve Me")

    def test_post_author_can_update_own_post(self):
        post = self.user.posts.create(title="Old Title", content="Old content")
        response = self.client.patch(reverse("post-detail", args=[post.id]), {"title": "Updated Title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")

    def test_different_user_cannot_update_post(self):
        post = self.user.posts.create(title="Owned", content="By user 1")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(reverse("post-detail", args=[post.id]), {"title": "Hacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_author_can_delete_own_post(self):
        post = self.user.posts.create(title="Delete me", content="Bye")
        response = self.client.delete(reverse("post-detail", args=[post.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_different_user_cannot_delete_post(self):
        post = self.user.posts.create(title="Protected", content="Do not delete")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(reverse("post-detail", args=[post.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_posts_by_author(self):
        self.user.posts.create(title="User 1 post", content="django stuff")
        self.other_user.posts.create(title="User 2 post", content="other content")
        response = self.client.get(reverse("post-list"), {"author": self.user.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["author"], self.user.id)

    def test_search_posts_by_title_and_content(self):
        self.user.posts.create(title="Django tutorial", content="Intro to Django")
        self.user.posts.create(title="Robots", content="Django rest api")
        self.user.posts.create(title="Other", content="Not match")
        response = self.client.get(reverse("post-list"), {"search": "django"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_pagination_returns_10_results_per_page(self):
        for i in range(25):
            self.user.posts.create(title=f"post-{i}", content=f"content-{i}")

        response = self.client.get(reverse("post-list"), {"page": 1}, format="json")
        page_2 = self.client.get(reverse("post-list"), {"page": 2}, format="json")
        page_3 = self.client.get(reverse("post-list"), {"page": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 25)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])
        self.assertEqual(len(page_2.data["results"]), 10)
        self.assertEqual(len(page_3.data["results"]), 5)

    def test_filter_search_and_pagination_work_together(self):
        self.user.posts.create(title="Django alpha", content="alpha")
        self.user.posts.create(title="Django beta", content="beta")
        self.user.posts.create(title="Other", content="django value")
        self.other_user.posts.create(title="Django gamma", content="not from user")
        response = self.client.get(reverse("post-list"), {"author": self.user.id, "search": "django", "page": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)
