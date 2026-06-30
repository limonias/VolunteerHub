import json

from django.test import TestCase
from django.urls import reverse


class AuthAndProfileSecurityTests(TestCase):
    def test_registration_creates_session_and_profile_is_private(self):
        payload = {
            "firstName": "Ada",
            "surname": "Lovelace",
            "email": "ada@example.com",
            "password": "securepass123",
            "age": 30,
            "phone": "+380501112233",
        }

        response = self.client.post(
            reverse("register_volunteer"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.session["user_id"], response.json()["userId"])

        profile_response = self.client.get(reverse("get_profile", kwargs={"user_id": response.json()["userId"]}))
        self.assertEqual(profile_response.status_code, 200)

    def test_profile_access_requires_authentication(self):
        user_payload = {
            "firstName": "Grace",
            "surname": "Hopper",
            "email": "grace@example.com",
            "password": "securepass123",
            "age": 40,
            "phone": "+380501112244",
        }

        register_response = self.client.post(
            reverse("register_volunteer"),
            data=json.dumps(user_payload),
            content_type="application/json",
        )
        user_id = register_response.json()["userId"]

        other_client = self.client_class()
        response = other_client.get(reverse("get_profile", kwargs={"user_id": user_id}))
        self.assertEqual(response.status_code, 401)
