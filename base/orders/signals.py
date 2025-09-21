from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cart
from users.models import UserProfile


# автосоздание корзины для нового польз

@receiver(post_save, sender=UserProfile)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.get_or_create(user=instance)

