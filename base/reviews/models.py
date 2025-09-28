from django.db import models
from users.models import UserProfile


def review_image_path(instance, filename):
    """Путь для сохранения картинок к отзывам"""
    return f"reviews/{instance.review.id}/{filename}"


class Review(models.Model):
    """Отзывы о лекарствах"""

    user = models.ForeignKey(
        UserProfile,
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
        constraints = [
            models.UniqueConstraint(
                fields=["user", "medicine"], name="unique_user_medicine_review"
            )
        ]

    def __str__(self):
        return f"{self.user} — {self.medicine} ({self.rating})"


class ReviewImage(models.Model):
    """Доп. изображения для отзывов"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Отзыв",
    )
    image = models.ImageField(
        upload_to=review_image_path,
        verbose_name="Изображение",
        blank=True,
        null=True,  # чтобы в базе можно было хранить NULL
    )

    def __str__(self):
        return f"Изображение для отзыва {self.review.id}"
