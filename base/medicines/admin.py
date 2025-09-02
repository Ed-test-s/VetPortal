from django.contrib import admin
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "manufacturer", "is_prescription", "updated_at")
    search_fields = ("name", "manufacturer")
    prepopulated_fields = {"slug": ("name",)}
