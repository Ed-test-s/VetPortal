from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_email", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "phone")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Логин"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"
