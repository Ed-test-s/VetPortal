from django.db import models, IntegrityError
from utils import generate_unique_slug
from django.db.models import Min


def medicine_main_image_path(instance, filename):
    return f"medicines/{instance.slug}/main/{filename}"


def medicine_extra_image_path(instance, filename):
    return f"medicines/{instance.medicine.slug}/extra/{filename}"


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
    main_image = models.ImageField(upload_to=medicine_main_image_path, blank=True, null=True)
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

    def get_min_price(self):
        """Вернёт минимальную цену лекарства среди аптек"""
        price = self.medicine_in_pharmacies.aggregate(min_price=Min("price"))["min_price"]
        return price if price is not None else None


class PharmacyImage(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=medicine_extra_image_path)
