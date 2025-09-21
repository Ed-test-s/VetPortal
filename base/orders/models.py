from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from django.utils import timezone
from users.models import UserProfile


class Cart(models.Model):
    """Корзина пользователя (одна на пользователя)."""
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.select_related("pharmacy_medicine"))

    def grouped_by_pharmacy(self):
        """Секции корзины по аптекам (для логики оформления по одной аптеке)."""
        from collections import defaultdict
        groups = defaultdict(list)
        qs = self.items.select_related(
            "pharmacy_medicine__pharmacy",
            "pharmacy_medicine__medicine"
        )
        for item in qs:
            groups[item.pharmacy_medicine.pharmacy].append(item)
        return groups


class CartItem(models.Model):
    """Позиция корзины — конкретное лекарство в конкретной аптеке."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    pharmacy_medicine = models.ForeignKey(
        "pharmacies.PharmacyMedicine",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Лекарство в аптеке"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ("cart", "pharmacy_medicine")
        indexes = [
            models.Index(fields=["cart", "pharmacy_medicine"]),
        ]

    def __str__(self):
        pm = self.pharmacy_medicine
        return f"{pm.medicine.name} ({pm.pharmacy.name}) x {self.quantity}"

    def clean(self):
        """Валидация доступности товара."""
        if self.pharmacy_medicine and hasattr(self.pharmacy_medicine, "is_available"):
            if not self.pharmacy_medicine.is_available(self.quantity):
                from django.core.exceptions import ValidationError
                raise ValidationError("Недостаточно товара в аптеке.")

    def total_price(self):
        price = self.pharmacy_medicine.price or 0
        return price * self.quantity


class Favorite(models.Model):
    """Избранное: пользователь ↔ лекарство (без услуг)."""
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="in_favorites"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Избранное (лекарство)"
        verbose_name_plural = "Избранное (лекарства)"
        unique_together = ("user", "medicine")
        indexes = [
            models.Index(fields=["user", "medicine"]),
        ]

    def __str__(self):
        return f"{self.user.user.username} ♥ {self.medicine.name}"

    @classmethod
    def toggle(cls, user, medicine):
        """Добавить/удалить из избранного. Возвращает (obj, created)."""
        favorite, created = cls.objects.get_or_create(user=user, medicine=medicine)
        if not created:
            favorite.delete()
            return None, False
        return favorite, True


class Order(models.Model):
    """Заказ: формируется из позиций одной аптеки."""
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_READY = "ready_for_pickup"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает подтверждения"),
        (STATUS_CONFIRMED, "Подтверждён"),
        (STATUS_READY, "Готов к выдаче"),
        (STATUS_COMPLETED, "Завершён"),
        (STATUS_CANCELLED, "Отменён"),
    ]

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    pharmacy = models.ForeignKey(
        "pharmacies.Pharmacy",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Аптека"
    )
    order_number = models.CharField(
        max_length=36,
        unique=True,
        editable=False,
        db_index=True
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    status_updated_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=500, blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["pharmacy", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Заказ {self.order_number} ({self.pharmacy.name})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.order_number:
            self.order_number = str(uuid.uuid4())
        if not is_new:
            old = Order.objects.filter(pk=self.pk).first()
            if old and old.status != self.status:
                self.status_updated_at = timezone.now()
        else:
            self.status_updated_at = timezone.now()

        # сначала сохраняем заказ, чтобы появился pk
        super().save(*args, **kwargs)

        # только потом пересчитываем total (если заказ уже существует)
        self.recalc_total(save=True)

    def recalc_total(self, save=True):
        total = sum(item.total_price() for item in self.items.all())
        self.total_price = total
        if save:
            super(Order, self).save(update_fields=["total_price"])
        return total


class OrderItem(models.Model):
    """Позиция заказа: фиксируем цену на момент покупки."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    pharmacy_medicine = models.ForeignKey(
        "pharmacies.PharmacyMedicine",
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Лекарство в аптеке"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        editable=False  # запрещаем редактировать вручную
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        indexes = [
            models.Index(fields=["order", "pharmacy_medicine"]),
        ]
        unique_together = ("order", "pharmacy_medicine")

    def save(self, *args, **kwargs):
        # фиксируем цену из PharmacyMedicine
        if not self.price_at_purchase and self.pharmacy_medicine:
            self.price_at_purchase = self.pharmacy_medicine.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pharmacy_medicine.medicine.name} x {self.quantity}"

    def total_price(self):
        return self.price_at_purchase * self.quantity

