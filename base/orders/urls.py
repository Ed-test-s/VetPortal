from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("success/", views.order_success, name="order_success"),
    path("history/", views.order_history, name="order_history"),

    path("cart/add/<int:pharmacy_medicine_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),

    path("favorites/", views.favorites_view, name="favorites"),
    path("favorites/toggle/<int:medicine_id>/", views.toggle_favorite, name="toggle_favorite"),
]
