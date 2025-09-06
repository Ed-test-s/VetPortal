from django.db import models
from utils import generate_unique_slug
from django.db import models, IntegrityError


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ("antibiotic", "Антибиотик"),
        ("vaccine", "Вакцина"),
        ("painkiller", "Обезболивающее"),
        ("vitamin", "Витамины"),
        ("other", "Другое"),
    ]

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other")
    manufacturer = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    instruction = models.TextField(blank=True)  # инструкция к применению
    is_prescription = models.BooleanField(default=False)
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
