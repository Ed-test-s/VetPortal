from django.contrib import admin
from django.utils.html import format_html
from .models import GroomingCenter, GroomingService, GroomingServiceImage

from users.models import UserProfile


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


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = UserProfile.objects.filter(role=UserProfile.ROLE_GROOMING)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
