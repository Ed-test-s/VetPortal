from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import UserProfile
from .models import Cart


# ✅ Автосоздание корзины для нового профиля
@receiver(post_save, sender=UserProfile)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.get_or_create(user=instance)
