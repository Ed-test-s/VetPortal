from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from pharmacies.models import PharmacyMedicine

class CustomUser(AbstractUser):
    ROLE_ADMIN_PORTAL = 'admin_portal'
    ROLE_CLIENT = 'client'
    ROLE_PHARMACY = 'pharmacy_admin'
    ROLE_CLINIC = 'clinic_admin'
    ROLE_GROOMING = 'grooming_admin'

    ROLE_CHOICES = [
        (ROLE_ADMIN_PORTAL, 'Администратор портала'),
        (ROLE_CLIENT, 'Обычный пользователь'),
        (ROLE_PHARMACY, 'Администратор аптеки'),
        (ROLE_CLINIC, 'Администратор клиники'),
        (ROLE_GROOMING, 'Администратор груминг-центра'),
    ]

    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default=ROLE_CLIENT)
    phone = models.CharField("Телефон", max_length=30, blank=True, null=True)
    org_name = models.CharField("Организация (если применимо)", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN_PORTAL


class Cart(models.Model):
    """Корзина пользователя"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def grouped_by_pharmacy(self):
        """Вернуть товары, сгруппированные по аптеке"""
        grouped = {}
        for item in self.items.select_related("pharmacy_medicine__pharmacy"):
            pharmacy = item.pharmacy_medicine.pharmacy
            if pharmacy not in grouped:
                grouped[pharmacy] = []
            grouped[pharmacy].append(item)
        return grouped


class CartItem(models.Model):
    """Позиция в корзине"""
    cart = models.ForeignKey("users.Cart", on_delete=models.CASCADE, related_name="items")
    pharmacy_medicine = models.ForeignKey(
        PharmacyMedicine, on_delete=models.CASCADE, verbose_name="Лекарство в аптеке"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        unique_together = ("cart", "pharmacy_medicine")

    def __str__(self):
        return f"{self.pharmacy_medicine.medicine.name} ({self.pharmacy_medicine.pharmacy.name}) x {self.quantity}"

    def total_price(self):
        return self.pharmacy_medicine.price * self.quantity

