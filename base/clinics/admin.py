from django.contrib import admin
from django.utils.html import format_html
from .models import Clinic, ClinicService, ClinicServiceImage

from users.models import UserProfile


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = UserProfile.objects.filter(role=UserProfile.ROLE_CLINIC)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
