from django.contrib import admin
from django.utils.html import format_html
from .models import Medicine, Category, PharmacyImage


class PharmacyImageInline(admin.TabularInline):
    model = PharmacyImage
    extra = 1
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return "—"
    preview.short_description = "Превью"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "manufacturer", "is_prescription", "updated_at", "main_preview")
    list_filter = ("category", "manufacturer")
    search_fields = ("name", "manufacturer")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PharmacyImageInline]

    def main_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.main_image.url)
        return "—"
    main_preview.short_description = "Основное фото"
