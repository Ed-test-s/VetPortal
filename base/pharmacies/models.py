from django.db import models
from django.conf import settings
from django.db import models, IntegrityError
from utils import generate_unique_slug
from users.models import UserProfile
from multiselectfield import MultiSelectField


DAYS_OF_WEEK = [
    ('mon', 'Понедельник'),
    ('tue', 'Вторник'),
    ('wed', 'Среда'),
    ('thu', 'Четверг'),
    ('fri', 'Пятница'),
    ('sat', 'Суббота'),
    ('sun', 'Воскресенье'),
]


class Pharmacy(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name="pharmacies")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    work_days = MultiSelectField(choices=DAYS_OF_WEEK, max_choices=7, blank=True)
    open_at = models.TimeField("Время открытия", null=False, blank=True)
    closed_at = models.TimeField("Время закрытия", null=False, blank=True)

    class Meta:
        unique_together = ("name", "address")
        ordering = ["name"]
        verbose_name = "Аптека"
        verbose_name_plural = "Аптеки"
        indexes = [models.Index(fields=["name"])]

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


class PharmacyMedicine(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="pharmacy_medicines")
    medicine = models.ForeignKey("medicines.Medicine", on_delete=models.CASCADE, related_name="medicine_in_pharmacies")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    in_stock = models.BooleanField(default=True)
    stock_qty = models.PositiveIntegerField(default=0, verbose_name="Количество")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("pharmacy", "medicine")
        ordering = ["-updated_at"]
        verbose_name_plural = "Склады аптек"

    def __str__(self):
        return f"{self.medicine.name} @ {self.pharmacy.name}"

    def is_available(self, qty=1):
        """Есть ли в наличии нужное количество"""
        return self.in_stock and self.stock_qty >= qty

