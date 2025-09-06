from django.contrib import admin
from .models import Clinic, ClinicService


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "owner", "is_active")
    search_fields = ("name", "address", "phone")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ClinicService)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "clinic", "price", "duration_minutes", "is_active")
    search_fields = ("name", "clinic__name")
    list_filter = ("is_active",)
