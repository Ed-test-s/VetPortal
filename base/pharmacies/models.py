from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Pharmacy(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name="pharmacies")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "address")
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PharmacyMedicine(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="pharmacy_medicines")
    medicine = models.ForeignKey("medicines.Medicine", on_delete=models.CASCADE, related_name="medicine_in_pharmacies")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    stock_qty = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("pharmacy", "medicine")
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["medicine"]), models.Index(fields=["pharmacy"])]

    def __str__(self):
        return f"{self.medicine.name} @ {self.pharmacy.name}"
