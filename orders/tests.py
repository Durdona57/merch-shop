from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from products.models import Category, Product
from .models import Order, OrderItem


class OrderCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Keychains", slug="keychains")
        self.product = Product.objects.create(
            category=self.category,
            name="Bunny Keychain",
            price=Decimal("15.00"),
            stock=5,
        )
        self.delivery_fields = {
            "full_name": "Jane Doe",
            "phone": "+1 555 000 0000",
            "street_address": "123 Pastel Lane",
            "city": "Springfield",
            "zip_code": "62701",
        }

    def test_successful_order_decrements_stock_and_computes_total(self):
        response = self.client.post(
            "/api/orders/",
            {**self.delivery_fields, "items": [{"product_id": self.product.id, "quantity": 2}]},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        order = Order.objects.get()
        self.assertEqual(order.total, Decimal("30.00"))
        self.assertEqual(OrderItem.objects.get(order=order).quantity, 2)

    def test_order_rejected_when_stock_insufficient(self):
        response = self.client.post(
            "/api/orders/",
            {**self.delivery_fields, "items": [{"product_id": self.product.id, "quantity": 999}]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)  # untouched
        self.assertEqual(Order.objects.count(), 0)

    def test_duplicate_product_id_is_aggregated_before_stock_check(self):
        """
        Bu eski xatolik (bug) qayta takrorlanmasligi uchun yozilgan test.
    Eski xatolikda: bitta mahsulot savatda ikkita alohida qatorda kelsa (masalan, 3 ta va 3 ta),
    tizim ularni umumiy (6 ta) deb emas, har birini alohida ombordagi qoldiqqa (5 taga) solishtirib,
    xaridga ruxsat berib yuborgan va ombor minusga kirib ketgan..
        """
        response = self.client.post(
            "/api/orders/",
            {
                **self.delivery_fields,
                "items": [
                    {"product_id": self.product.id, "quantity": 3},
                    {"product_id": self.product.id, "quantity": 3},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Order.objects.count(), 0)

    def test_duplicate_product_id_within_available_stock_succeeds_as_one_line(self):
        response = self.client.post(
            "/api/orders/",
            {
                **self.delivery_fields,
                "items": [
                    {"product_id": self.product.id, "quantity": 2},
                    {"product_id": self.product.id, "quantity": 1},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)  # 5 - (2+1)
        self.assertEqual(OrderItem.objects.filter(order=Order.objects.get()).count(), 1)

    def test_price_snapshot_is_unaffected_by_later_price_changes(self):
        response = self.client.post(
            "/api/orders/",
            {**self.delivery_fields, "items": [{"product_id": self.product.id, "quantity": 1}]},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        # Price changes after the order was placed
        self.product.price = Decimal("99.00")
        self.product.save()

        order_item = OrderItem.objects.get(order=Order.objects.get())
        self.assertEqual(order_item.price, Decimal("15.00"))
        self.assertEqual(order_item.product_name, "Bunny Keychain")

    def test_empty_cart_is_rejected(self):
        response = self.client.post(
            "/api/orders/", {**self.delivery_fields, "items": []}, format="json"
        )
        self.assertEqual(response.status_code, 400)
