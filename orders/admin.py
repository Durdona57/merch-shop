from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "price", "quantity"]
    can_delete = False


@admin.action(description="Mark selected orders as paid")
def mark_as_paid(modeladmin, request, queryset):
    queryset.update(status="paid")


@admin.action(description="Mark selected orders as shipped")
def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status="shipped")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "phone", "total", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["full_name", "phone"]
    inlines = [OrderItemInline]
    actions = [mark_as_paid, mark_as_shipped]
