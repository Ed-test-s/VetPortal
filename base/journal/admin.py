from django.contrib import admin
from .models import Category, Tag, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)
    exclude = ("slug",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_at", "updated_at", "is_published")
    list_filter = ("category", "tags", "created_at", "is_published")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)

    fieldsets = (
        (None, {
            "fields": (
                "title", "author", "published_at", "image",
                "slug", "content", "zip_file"   # ← тут заменил
            ),
            "description": (
                "⚠️ Если вы загружаете архив статьи (.zip), он должен содержать:<br>"
                "- <b>index.html</b> — основной файл<br>"
                "- <b>style.css</b> (опционально)<br>"
                "- папку <b>images/</b> для картинок<br>"
                "⚠️ Пути в index.html должны быть относительными (например: images/img1.jpg)."
            )
        }),
    )
