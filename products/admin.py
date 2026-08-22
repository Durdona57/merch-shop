from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "sold_out_badge", "is_new_arrival"]
    list_filter = ["category", "is_new_arrival"]
    search_fields = ["name"]
    list_editable = ["price", "stock"]

    @admin.display(description="Status")
    def sold_out_badge(self, obj):
        return "Sold out" if obj.is_sold_out else "In stock"
