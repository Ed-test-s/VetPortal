from django.conf import settings
from django.db import models


class Review(models.Model):
    """Отзывы о лекарствах"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Лекарство",
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Оценка",
        help_text="Оценка от 1 до 5"
    )
    text = models.TextField("Текст отзыва", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.user} — {self.medicine} ({self.rating})"
