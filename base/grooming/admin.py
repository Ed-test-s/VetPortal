from django.contrib import admin
from .models import GroomingCenter, GroomingService


@admin.register(GroomingCenter)
class GroomingCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "address", "phone")


@admin.register(GroomingService)
class GroomingServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "center", "price", "duration_minutes", "is_active")
    autocomplete_fields = ("center",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
