import os
import zipfile
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.timezone import now
from utils import generate_unique_slug


def article_zip_path(instance, filename):
    return f"articles/{instance.slug}/{filename}"


def article_preview_path(instance, filename):
    return f"articles/{instance.slug}/preview/{filename}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Слаг", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, "slug", "name")
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            self.slug = generate_unique_slug(self, "slug", "name")
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")
    slug = models.SlugField(unique=True, verbose_name="Слаг", blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, "slug", "name")
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            self.slug = generate_unique_slug(self, "slug", "name")
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="Слаг", blank=True)

    # два варианта: текстовый или загруженный архив
    content = models.TextField(verbose_name="Содержимое", blank=True)
    zip_file = models.FileField(
        upload_to=article_zip_path,
        blank=True,
        null=True,
        verbose_name="ZIP архив со статьёй"
    )

    image = models.ImageField(
        upload_to=article_preview_path,
        blank=True,
        null=True,
        verbose_name="Превью (для списка статей)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Категория"
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name="articles",
        verbose_name="Теги"
    )

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, "slug", "title")

        if self.is_published and not self.published_at:
            self.published_at = now()

        super().save(*args, **kwargs)

        # если загрузили архив → распаковываем
        if self.zip_file:
            self.extract_zip()

    def extract_zip(self):
        """Распаковывает архив в media/articles/<slug>/"""
        extract_dir = os.path.join(settings.MEDIA_ROOT, "articles", self.slug)
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(self.zip_file.path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

    def has_archive(self):
        return bool(self.zip_file)

    def __str__(self):
        return self.title
