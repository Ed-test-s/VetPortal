from django.contrib import admin
from .models import Category, Tag, Article


class TagInline(admin.TabularInline):  # можно использовать StackedInline для другого вида
    model = Article.tags.through  # связывающая таблица ManyToMany
    extra = 1  # сколько пустых полей будет для добавления тегов


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_at", "updated_at")
    list_filter = ("category", "tags", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)  # красивый виджет для выбора тегов
    inlines = [TagInline]  # добавляем inline-редактирование тегов
