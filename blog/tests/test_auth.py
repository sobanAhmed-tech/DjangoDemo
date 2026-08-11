from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAPITests(APITestCase):
    def test_register_success(self):
        url = reverse("register")
        data = {
            "username": "soban",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "soban")
        self.assertNotIn("password", response.data)

    def test_register_password_mismatch(self):
        url = reverse("register")
        data = {
            "username": "soban2",
            "password": "StrongPassword123",
            "password2": "DifferentPassword123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(username="existing", password="StrongPassword123")
        url = reverse("register")
        data = {
            "username": "existing",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username="login_user", password="StrongPassword123")
        url = reverse("login")

        response = self.client.post(url, {"username": "login_user", "password": "StrongPassword123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        User.objects.create_user(username="refresh_user", password="StrongPassword123")
        login_response = self.client.post(
            reverse("login"),
            {"username": "refresh_user", "password": "StrongPassword123"},
            format="json",
        )

        response = self.client.post(reverse("token_refresh"), {"refresh": login_response.data["refresh"]}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
