from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

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

    phone = PhoneNumberField("Телефон", blank=True, null=True, region="BY", unique=True)
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default=ROLE_CLIENT, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["role"])]
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN_PORTAL
