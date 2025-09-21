from django.contrib import admin
from django.utils.html import format_html
from .models import GroomingCenter, GroomingService, GroomingServiceImage


class GroomingServiceImageInline(admin.TabularInline):
    model = GroomingServiceImage
    extra = 1
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return "—"
    preview.short_description = "Превью"


@admin.register(GroomingCenter)
class GroomingCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "address", "phone")


@admin.register(GroomingService)
class GroomingServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "center", "price", "duration_minutes", "is_active", "main_preview")
    autocomplete_fields = ("center",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [GroomingServiceImageInline]

    def main_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.main_image.url)
        return "—"
    main_preview.short_description = "Основное фото"
