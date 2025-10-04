from django.db import models
from django.conf import settings
from django.db import IntegrityError
from utils import generate_unique_slug
from phonenumber_field.modelfields import PhoneNumberField
from users.models import UserProfile
from multiselectfield import MultiSelectField


def clinic_service_main_image_path(instance, filename):
    return f"clinics/{instance.clinic.slug}/{instance.slug}/main/{filename}"


def clinic_service_extra_image_path(instance, filename):
    return f"clinics/{instance.service.clinic.slug}/{instance.service.slug}/extra/{filename}"


DAYS_OF_WEEK = [
    ('mon', 'Понедельник'),
    ('tue', 'Вторник'),
    ('wed', 'Среда'),
    ('thu', 'Четверг'),
    ('fri', 'Пятница'),
    ('sat', 'Суббота'),
    ('sun', 'Воскресенье'),
]


class Clinic(models.Model):
    owner = models.OneToOneField(UserProfile, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name="clinics")
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

    work_days = MultiSelectField(choices=DAYS_OF_WEEK, max_choices=7, blank=True)
    open_at = models.TimeField("Время открытия", null=False, blank=True)
    closed_at = models.TimeField("Время закрытия", null=False, blank=True)

    def clean(self):
        # Проверка: владелец уже где-то админ клиники?
        if self.owner and Clinic.objects.exclude(id=self.id).filter(owner=self.owner).exists():
            raise ValidationError("Этот пользователь уже является администратором другой клиники.")

        # Проверка: у юзера правильная роль
        if self.owner and self.owner.role != UserProfile.ROLE_CLINIC:
            raise ValidationError("Владелец клиники должен иметь роль 'Администратор клиники'.")

    class Meta:
        unique_together = ("name", "address")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["latitude", "longitude"])
        ]
        ordering = ["name"]
        verbose_name = "Ветеринарная клиника"
        verbose_name_plural = "Ветеринарные клиники"

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


class ClinicService(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    main_image = models.ImageField(upload_to=clinic_service_main_image_path, blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('clinic', 'slug')
        ordering = ["name"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        indexes = [models.Index(fields=["name"]), models.Index(fields=["clinic"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, "slug", "name")
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            self.slug = generate_unique_slug(self, "slug", "name")
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.clinic.name})"


class ClinicServiceImage(models.Model):
    service = models.ForeignKey(ClinicService, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=clinic_service_extra_image_path)
