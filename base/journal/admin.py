from django.contrib import admin
from .models import Category, Tag, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)  # тут тоже надо будет если что "slug" добавит
    # скрытие slug при редактировании/создании, под будущий функционал
    exclude = ("slug",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_at", "updated_at")
    list_filter = ("category", "tags", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)  # красивый виджет для выбора тегов
