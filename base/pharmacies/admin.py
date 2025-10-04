from django.contrib import admin
from .models import Pharmacy, PharmacyMedicine

from users.models import UserProfile


class PharmacyMedicineInline(admin.TabularInline):
    model = PharmacyMedicine
    extra = 1
    autocomplete_fields = ("medicine",)
    fields = ("medicine", "price", "in_stock", "stock_qty", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = UserProfile.objects.filter(role=UserProfile.ROLE_PHARMACY)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    search_fields = ("name", "address", "phone")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PharmacyMedicineInline]


@admin.register(PharmacyMedicine)
class PharmacyMedicineAdmin(admin.ModelAdmin):
    list_display = ("pharmacy", "medicine", "price", "in_stock", "stock_qty", "updated_at")
    list_filter = ("pharmacy", "in_stock")
    search_fields = ("pharmacy__name", "medicine__name")
    autocomplete_fields = ("pharmacy", "medicine")
    readonly_fields = ("updated_at",)
