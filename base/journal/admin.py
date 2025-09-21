from django.contrib import admin
from .models import Category, Tag, Article, Comment


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
                "title", "slug", "author", "published_at", "image",
                 "content", "zip_file"
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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("text", "user__user__username", "article__title")
    list_filter = ("created_at",)