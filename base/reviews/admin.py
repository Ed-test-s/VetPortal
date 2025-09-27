from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return "—"

    preview.short_description = "Превью"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "medicine", "rating", "created_at", "has_images")
    list_filter = ("rating", "created_at")
    search_fields = ("user__user__username", "medicine__name", "text")  # ⚡ у тебя UserProfile, поэтому user__user__username
    inlines = [ReviewImageInline]

    def has_images(self, obj):
        return obj.images.exists()
    has_images.boolean = True
    has_images.short_description = "Есть картинки"
