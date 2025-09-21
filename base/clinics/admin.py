from django.contrib import admin
from django.utils.html import format_html
from .models import Clinic, ClinicService, ClinicServiceImage


class ClinicServiceImageInline(admin.TabularInline):
    model = ClinicServiceImage
    extra = 1
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return "—"
    preview.short_description = "Превью"


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")
    search_fields = ("name", "address", "phone")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ClinicService)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "clinic", "price", "duration_minutes", "is_active", "main_preview")
    search_fields = ("name", "clinic__name")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ClinicServiceImageInline]

    def main_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.main_image.url)
        return "—"
    main_preview.short_description = "Основное фото"
