from django.db import models
from django.conf import settings
from django.db import IntegrityError
from utils import generate_unique_slug
from phonenumber_field.modelfields import PhoneNumberField
from users.models import UserProfile


def grooming_service_main_image_path(instance, filename):
    return f"grooming/{instance.center.slug}/{instance.slug}/main/{filename}"


def grooming_service_extra_image_path(instance, filename):
    return f"grooming/{instance.service.center.slug}/{instance.service.slug}/extra/{filename}"


class GroomingCenter(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name="grooming_centers")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    address = models.CharField(max_length=500)
    phone = PhoneNumberField(region="BY")
    email = models.EmailField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
        ]
        ordering = ["name"]
        verbose_name = "Груминг-центр"
        verbose_name_plural = "Груминг-центры"

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


class GroomingService(models.Model):
    center = models.ForeignKey(GroomingCenter, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    main_image = models.ImageField(upload_to=grooming_service_main_image_path, blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("center", "slug")
        ordering = ["name"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, "slug", "name")
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            self.slug = generate_unique_slug(self, "slug", "name")
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.center.name}: {self.name}"


class GroomingServiceImage(models.Model):
    service = models.ForeignKey(GroomingService, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=grooming_service_extra_image_path)
