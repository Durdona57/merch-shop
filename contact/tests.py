from django.test import TestCase
from rest_framework.test import APIClient
from .models import ContactMessage


class ContactMessageTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_valid_message_is_saved(self):
        response = self.client.post(
            "/api/contact/",
            {"name": "Jane", "email": "jane@example.com", "message": "Love the shop!"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_missing_email_is_rejected(self):
        response = self.client.post(
            "/api/contact/",
            {"name": "Jane", "message": "Love the shop!"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
