from django.contrib import admin
from .models import GroomingCenter, GroomingService


@admin.register(GroomingCenter)
class GroomingCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(GroomingService)
class GroomingServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "center", "price", "duration_minutes", "is_active")
