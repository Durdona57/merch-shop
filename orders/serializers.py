from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from products.models import Product
from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)
    order_items = OrderItemOutputSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "full_name", "phone", "street_address", "city", "zip_code",
            "status", "total", "created_at", "items", "order_items",
        ]
        read_only_fields = ["id", "status", "total", "created_at"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Cart is empty.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        aggregated_quantities: dict[int, int] = defaultdict(int)
        for item in items_data:
            aggregated_quantities[item["product_id"]] += item["quantity"]

        with transaction.atomic():
            products = {
                p.id: p
                for p in Product.objects.select_for_update().filter(
                    id__in=aggregated_quantities.keys()
                )
            }

            order_items = []
            total = Decimal("0.00")

            for product_id, quantity in aggregated_quantities.items():
                product = products.get(product_id)
                if product is None:
                    raise serializers.ValidationError(
                        f"Product {product_id} does not exist."
                    )
                if product.stock < quantity:
                    raise serializers.ValidationError(
                        f"'{product.name}' only has {product.stock} left in stock."
                    )
                total += product.price * quantity
                order_items.append((product, quantity))

            order = Order.objects.create(total=total, **validated_data)

            for product, quantity in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=quantity,
                )
                product.stock -= quantity
                product.save(update_fields=["stock"])

            return order
