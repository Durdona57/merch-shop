from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Category, Product


class ProductListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.keychains = Category.objects.create(name="Keychains", slug="keychains")
        self.mugs = Category.objects.create(name="Mugs", slug="mugs")
        self.in_stock = Product.objects.create(
            category=self.keychains, name="Bunny Keychain", price=Decimal("15.00"), stock=5
        )
        self.sold_out = Product.objects.create(
            category=self.mugs, name="Moon Mug", price=Decimal("20.00"), stock=0
        )

    def test_list_returns_all_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_category_filter(self):
        response = self.client.get("/api/products/?category=keychains")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Bunny Keychain")

    def test_is_sold_out_reflects_stock(self):
        response = self.client.get("/api/products/")
        by_name = {p["name"]: p for p in response.data}
        self.assertFalse(by_name["Bunny Keychain"]["is_sold_out"])
        self.assertTrue(by_name["Moon Mug"]["is_sold_out"])
