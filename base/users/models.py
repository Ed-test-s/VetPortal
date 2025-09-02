from django.contrib.auth.models import AbstractUser
from django.db import models


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
