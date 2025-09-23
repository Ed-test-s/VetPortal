from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("success/", views.order_success, name="order_success"),
    path("favorites/", views.favorites_view, name="favorites"),
]

