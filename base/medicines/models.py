from django.db import models, IntegrityError
from utils import generate_unique_slug


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Слаг")

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


class Medicine(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Слаг")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
        verbose_name="Категория"
    )
    manufacturer = models.CharField(max_length=255, blank=True, verbose_name="Производитель")
    description = models.TextField(blank=True, verbose_name="Описание")
    instruction = models.TextField(blank=True, verbose_name="Инструкция по применению")
    is_prescription = models.BooleanField(default=False, verbose_name="Требует рецепт")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]
        ordering = ["name"]
        verbose_name = "Лекарство"
        verbose_name_plural = "Лекарства"

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
