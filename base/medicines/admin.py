from django.contrib import admin
from .models import Medicine, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "manufacturer", "is_prescription", "updated_at")
    search_fields = ("name", "manufacturer")
    prepopulated_fields = {"slug": ("name",)}
