from django.contrib import admin
from .models import Pharmacy, PharmacyMedicine


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")
    search_fields = ("name", "address", "phone")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PharmacyMedicine)
class PharmacyMedicineAdmin(admin.ModelAdmin):
    list_display = ("pharmacy", "medicine", "price", "in_stock", "stock_qty", "updated_at")
    list_filter = ("in_stock",)
    search_fields = ("pharmacy__name", "medicine__name")
