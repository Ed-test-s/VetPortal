from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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
    phone = PhoneNumberField("Телефон", blank=True, null=True, region="BY", unique=True)
    org_name = models.CharField("Организация (если применимо)", max_length=255, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["role"])]
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN_PORTAL


